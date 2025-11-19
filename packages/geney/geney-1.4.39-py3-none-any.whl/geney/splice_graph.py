# oncosplice/splice_graph.py
from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, Generator, List, Tuple

import numpy as np
import pandas as pd
from pandas import Series

from .utils import short_hash_of_list  # type: ignore


class SpliceSimulator:
    """
    Builds a splice-site graph from a splicing DataFrame and enumerates isoform paths.
    """

    def __init__(self, splicing_df: pd.DataFrame, transcript, max_distance: int, feature: str = "event"):
        self.full_df = splicing_df
        self.feature = feature
        self.rev = transcript.rev
        self.transcript_start = transcript.transcript_start
        self.transcript_end = transcript.transcript_end
        self.donors = transcript.donors
        self.acceptors = transcript.acceptors
        self.transcript = transcript
        self.max_distance = max_distance

        self.set_donor_nodes()
        self.set_acceptor_nodes()

    def _compute_splice_df(self, site_type: str) -> pd.DataFrame:
        feature_col = f"{self.feature}_prob"
        df = getattr(self.full_df, site_type + "s").copy()
        site_set = getattr(self, site_type + "s")

        missing = set(site_set) - set(df.index)
        if missing:
            df = pd.concat([df, pd.DataFrame(index=list(missing))], axis=0)
            df.loc[list(missing), ["annotated", "ref_prob", feature_col]] = [True, 1, 1]

        if "annotated" not in df.columns:
            df["annotated"] = False
        else:
            df["annotated"] = df["annotated"].where(df["annotated"].notna(), False).astype(bool)

        df.sort_index(ascending=not self.rev, inplace=True)

        MIN_INCREASE_RATIO = 0.2

        df["discovered_delta"] = np.where(
            ~df["annotated"],
            (df[feature_col] - df["ref_prob"]),
            np.nan,
        )
        df["discovered_delta"] = df["discovered_delta"].where(
            df["discovered_delta"] >= MIN_INCREASE_RATIO, 0
        )

        with np.errstate(divide="ignore", invalid="ignore"):
            df["deleted_delta"] = np.where(
                (df["ref_prob"] > 0) & df["annotated"],
                (df[feature_col] - df["ref_prob"]) / df["ref_prob"],
                0,
            )
        df["deleted_delta"] = df["deleted_delta"].clip(upper=0)

        df["P"] = df["annotated"].astype(float) + df["discovered_delta"] + df["deleted_delta"]
        return df

    @property
    def donor_df(self) -> pd.DataFrame:
        return self._compute_splice_df("donor")

    @property
    def acceptor_df(self) -> pd.DataFrame:
        return self._compute_splice_df("acceptor")

    def report(self, pos):
        metadata = self.find_splice_site_proximity(pos)
        metadata["donor_events"] = self.donor_df[
            (self.donor_df.deleted_delta.abs() > 0.2)
            | (self.donor_df.discovered_delta.abs() > 0.2)
        ].reset_index().to_json()
        metadata["acceptor_events"] = self.acceptor_df[
            (self.acceptor_df.deleted_delta.abs() > 0.2)
            | (self.acceptor_df.discovered_delta.abs() > 0.2)
        ].reset_index().to_json()
        metadata["missplicing"] = self.max_splicing_delta("event_prob")
        return metadata

    def max_splicing_delta(self, event: str) -> float:
        all_diffs = []
        for site_type in ["donors", "acceptors"]:
            df = self.full_df[site_type]
            diffs = (df[event] - df["ref_prob"]).tolist()
            all_diffs.extend(diffs)
        return max(all_diffs, key=abs)

    def set_donor_nodes(self) -> None:
        donors = self.donor_df.P
        donor_list = list(donors[donors > 0].round(2).items())
        donor_list.append((self.transcript_end, 1))
        self.donor_nodes = sorted(
            donor_list, key=lambda x: int(x[0]), reverse=bool(self.rev)
        )

    def set_acceptor_nodes(self) -> None:
        acceptors = self.acceptor_df.P
        acceptor_list = list(acceptors[acceptors > 0].round(2).items())
        acceptor_list.insert(0, (self.transcript_start, 1.0))
        self.acceptor_nodes = sorted(
            acceptor_list, key=lambda x: int(x[0]), reverse=bool(self.rev)
        )

    def generate_graph(self) -> Dict[Tuple[int, str], List[Tuple[int, str, float]]]:
        adjacency_list: Dict[Tuple[int, str], List[Tuple[int, str, float]]] = defaultdict(list)

        # donor -> acceptor
        for d_pos, d_prob in self.donor_nodes:
            running_prob = 1.0
            for a_pos, a_prob in self.acceptor_nodes:
                correct_orientation = ((a_pos > d_pos and not self.rev) or (a_pos < d_pos and self.rev))
                distance_valid = abs(a_pos - d_pos) <= self.max_distance
                if not (correct_orientation and distance_valid):
                    continue

                if not self.rev:
                    in_between_acceptors = sum(1 for a, _ in self.acceptor_nodes if d_pos < a < a_pos)
                    in_between_donors = sum(1 for d, _ in self.donor_nodes if d_pos < d < a_pos)
                else:
                    in_between_acceptors = sum(1 for a, _ in self.acceptor_nodes if a_pos < a < d_pos)
                    in_between_donors = sum(1 for d, _ in self.donor_nodes if a_pos < d < d_pos)

                if in_between_donors == 0 or in_between_acceptors == 0:
                    adjacency_list[(d_pos, "donor")].append((a_pos, "acceptor", a_prob))
                    running_prob -= a_prob
                else:
                    if running_prob > 0:
                        adjacency_list[(d_pos, "donor")].append(
                            (a_pos, "acceptor", a_prob * running_prob)
                        )
                        running_prob -= a_prob
                    else:
                        break

        # acceptor -> donor
        for a_pos, a_prob in self.acceptor_nodes:
            running_prob = 1.0
            for d_pos, d_prob in self.donor_nodes:
                correct_orientation = ((d_pos > a_pos and not self.rev) or (d_pos < a_pos and self.rev))
                distance_valid = abs(d_pos - a_pos) <= self.max_distance
                if not (correct_orientation and distance_valid):
                    continue

                if not self.rev:
                    in_between_acceptors = sum(1 for a, _ in self.acceptor_nodes if a_pos < a < d_pos)
                    in_between_donors = sum(1 for d, _ in self.donor_nodes if a_pos < d < d_pos)
                else:
                    in_between_acceptors = sum(1 for a, _ in self.acceptor_nodes if d_pos < a < a_pos)
                    in_between_donors = sum(1 for d, _ in self.donor_nodes if d_pos < d < a_pos)

                tag = "donor" if d_pos != self.transcript_end else "transcript_end"
                if in_between_acceptors == 0:
                    adjacency_list[(a_pos, "acceptor")].append((d_pos, tag, d_prob))
                    running_prob -= d_prob
                else:
                    if running_prob > 0:
                        adjacency_list[(a_pos, "acceptor")].append(
                            (d_pos, tag, d_prob * running_prob)
                        )
                        running_prob -= d_prob
                    else:
                        break

        # transcript_start -> donors
        running_prob = 1.0
        for d_pos, d_prob in self.donor_nodes:
            correct_orientation = (
                (d_pos > self.transcript_start and not self.rev)
                or (d_pos < self.transcript_start and self.rev)
            )
            distance_valid = abs(d_pos - self.transcript_start) <= self.max_distance
            if correct_orientation and distance_valid:
                adjacency_list[(self.transcript_start, "transcript_start")].append(
                    (d_pos, "donor", d_prob)
                )
                running_prob -= d_prob
                if running_prob <= 0:
                    break

        # normalize outgoing edges
        for key, next_nodes in adjacency_list.items():
            total_prob = sum(prob for (_, _, prob) in next_nodes)
            if total_prob > 0:
                adjacency_list[key] = [
                    (pos, typ, round(prob / total_prob, 3))
                    for pos, typ, prob in next_nodes
                ]
        return adjacency_list

    def find_all_paths(
        self,
        graph: Dict[Tuple[int, str], List[Tuple[int, str, float]]],
        start: Tuple[int, str],
        end: Tuple[int, str],
        path: List[Tuple[int, str]] | None = None,
        probability: float = 1.0,
    ) -> Generator[Tuple[List[Tuple[int, str]], float], None, None]:
        if path is None:
            path = [start]
        else:
            path = path + [start]

        if start == end:
            yield path, probability
            return
        if start not in graph:
            return

        for next_pos, tag, prob in graph[start]:
            yield from self.find_all_paths(
                graph,
                (next_pos, tag),
                end,
                path,
                probability * prob,
            )

    def get_viable_paths(self) -> List[Tuple[List[Tuple[int, str]], float]]:
        graph = self.generate_graph()
        start_node = (self.transcript_start, "transcript_start")
        end_node = (self.transcript_end, "transcript_end")
        paths = list(self.find_all_paths(graph, start_node, end_node))
        paths.sort(key=lambda x: x[1], reverse=True)
        return paths

    def get_viable_transcripts(self, metadata: bool = False):
        graph = self.generate_graph()
        start_node = (self.transcript_start, "transcript_start")
        end_node = (self.transcript_end, "transcript_end")
        paths = list(self.find_all_paths(graph, start_node, end_node))
        paths.sort(key=lambda x: x[1], reverse=True)

        for path, prob in paths:
            donors = [pos for pos, typ in path if typ == "donor"]
            acceptors = [pos for pos, typ in path if typ == "acceptor"]

            t = self.transcript.clone()
            t.donors = [d for d in donors if d != t.transcript_end]
            t.acceptors = [a for a in acceptors if a != t.transcript_start]
            t.path_weight = prob
            t.path_hash = short_hash_of_list(tuple(donors + acceptors))
            t.generate_mature_mrna().generate_protein()
            if metadata:
                md = pd.concat(
                    [
                        self.compare_splicing_to_reference(t),
                        pd.Series(
                            {
                                "isoform_prevalence": t.path_weight,
                                "isoform_id": t.path_hash,
                            }
                        ),
                    ]
                )
                yield t, md
            else:
                yield t

    def find_splice_site_proximity(self, pos: int) -> Series:
        def result(region, index, start, end):
            return pd.Series(
                {
                    "region": region,
                    "index": index + 1,
                    "5'_dist": abs(pos - min(start, end)),
                    "3'_dist": abs(pos - max(start, end)),
                }
            )

        if not hasattr(self.transcript, "exons") or not hasattr(self.transcript, "introns"):
            return pd.Series(
                {"region": None, "index": None, "5'_dist": np.inf, "3'_dist": np.inf}
            )

        for i, (start, end) in enumerate(self.transcript.exons):
            if min(start, end) <= pos <= max(start, end):
                return result("exon", i, start, end)

        for i, (start, end) in enumerate(self.transcript.introns):
            if min(start, end) <= pos <= max(start, end):
                return result("intron", i, start, end)

        return pd.Series(
            {"region": None, "index": None, "5'_dist": np.inf, "3'_dist": np.inf}
        )

    def define_missplicing_events(self, var) -> Tuple[str, str, str, str, str]:
        ref = self.transcript
        ref_introns, ref_exons = getattr(ref, "introns", []), getattr(ref, "exons", [])
        var_introns, var_exons = getattr(var, "introns", []), getattr(var, "exons", [])

        num_ref_exons = len(ref_exons)
        num_ref_introns = len(ref_introns)

        pes, pir, es, ne, ir = [], [], [], [], []

        for exon_count, (t1, t2) in enumerate(ref_exons):
            for (s1, s2) in var_exons:
                if (not ref.rev and ((s1 == t1 and s2 < t2) or (s1 > t1 and s2 == t2))) or (
                    ref.rev and ((s1 == t1 and s2 > t2) or (s1 < t1 and s2 == t2))
                ):
                    pes.append(
                        f"Exon {exon_count+1}/{num_ref_exons} truncated: {(t1, t2)} --> {(s1, s2)}"
                    )

        for intron_count, (t1, t2) in enumerate(ref_introns):
            for (s1, s2) in var_introns:
                if (not ref.rev and ((s1 == t1 and s2 < t2) or (s1 > t1 and s2 == t2))) or (
                    ref.rev and ((s1 == t1 and s2 > t2) or (s1 < t1 and s2 == t2))
                ):
                    pir.append(
                        f"Intron {intron_count+1}/{num_ref_introns} partially retained: {(t1, t2)} --> {(s1, s2)}"
                    )

        for exon_count, (t1, t2) in enumerate(ref_exons):
            if t1 not in var.acceptors and t2 not in var.donors:
                es.append(
                    f"Exon {exon_count+1}/{num_ref_exons} skipped: {(t1, t2)}"
                )

        for (s1, s2) in var_exons:
            if s1 not in ref.acceptors and s2 not in ref.donors:
                ne.append(f"Novel Exon: {(s1, s2)}")

        for intron_count, (t1, t2) in enumerate(ref_introns):
            if t1 not in var.donors and t2 not in var.acceptors:
                ir.append(
                    f"Intron {intron_count+1}/{num_ref_introns} retained: {(t1, t2)}"
                )

        return ",".join(pes), ",".join(pir), ",".join(es), ",".join(ne), ",".join(ir)

    def summarize_missplicing_event(self, pes, pir, es, ne, ir) -> str:
        event = []
        if pes:
            event.append("PES")
        if es:
            event.append("ES")
        if pir:
            event.append("PIR")
        if ir:
            event.append("IR")
        if ne:
            event.append("NE")
        return ",".join(event) if event else "-"

    def compare_splicing_to_reference(self, transcript_variant) -> Series:
        pes, pir, es, ne, ir = self.define_missplicing_events(transcript_variant)
        return pd.Series(
            {
                "pes": pes,
                "pir": pir,
                "es": es,
                "ne": ne,
                "ir": ir,
                "summary": self.summarize_missplicing_event(pes, pir, es, ne, ir),
            }
        )