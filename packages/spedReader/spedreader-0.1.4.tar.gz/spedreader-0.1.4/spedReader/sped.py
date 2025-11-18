""" Module containing the Sped class and its helper Block class. """
import numpy as np
import pandas as pd

class Block:
    """ A block of a SPED file. """
    def __init__(self, name: str, data: dict[str, pd.DataFrame]):
        self.name = name
        self.registries = data

    def get_registry(self, registry: str) -> pd.DataFrame:
        return self.registries[registry]

    def __getitem__(self, registry: str) -> pd.DataFrame:
        """ Allow for dictionary style access. """
        return self.registries[registry]

    def __repr__(self) -> str:
        return f"Block(name={self.name}, registries={list(self.registries.keys())})"

class Sped:
    """ The SPED class. """
    def __init__(self):
        self.blocks: dict[str, Block] = {}

    def add_block(self, block: Block) -> None:
        self.blocks[block.name] = block

    def get_block(self, name: str):
        return self.blocks[name]

    def is_valid(self):
        # TODO Check documentation for comprehensive list of mandatory columns.
        mandatory_columns = {"reg", "cnpj", "ind_oper", "ind_emit", "cod_part",
                            "cod_mod", "cod_sit", "num_doc", "dt_doc", "vl_doc", "ind_pgto", "ind_frt",
                            "num_item", "cod_item", "vl_item", "cfop", "cst_pis", "cst_cofins", "vl_opr",
                            "vl_pis", "vl_cofins", "cod_inf", "num_proc", "ind_proc", "cod_doc_imp",
                            "num_doc_imp", "dt_doc_ini", "dt_doc_fin", "vl_tot_item",
                            "dt_ref_ini", "dt_ref_fin", "vl_doc_canc"}
        for block in self.blocks:
            for registry in self.blocks[block].registries:
                # This provides an intersection between the dataframe columns and the mandatory columns.
                columns_to_verify = set(self.blocks[block].registries[registry].columns) & mandatory_columns
                for column in columns_to_verify:
                    if '' in self.blocks[block].registries[registry][column]:
                        return False
        return True

    def _get_table(self, block, registry, parent_id=None, parent_index=None):
        """ Returns a table (DataFrame) according to search parameters.
            Return None if nothing is found. """
        try:
            if parent_id is not None and parent_index is not None:
                if isinstance(parent_index, pd.Series):
                    parent_index = parent_index.iloc[0]
                return self.blocks[block][registry].query(f"{parent_id} == @parent_index").copy()
            return self.blocks[block][registry].copy()
        except KeyError:
            return None

    def _save_table(self, file_name, table, registry, column_id, parent_id=None):
        if table is not None:
            table = table.astype("object")
            table[column_id] = f"|{registry}"
            if parent_id:
                table = table.drop(parent_id, axis=1)
            with open(file_name, "a", encoding="utf-8") as fp:
                np.savetxt(fp, table, delimiter="|", fmt="%s")

    def write_sped(self, filename):
        """ Writes a SPED file based on memory contents. """

        # Start of block 0.
        table = self._get_table("Bloco 0", "0000")
        self._save_table(filename, table, "0000", "id_0000")

        table = self._get_table("Bloco 0", "0001", "id_0000", 1)
        self._save_table(filename, table, "0001", "id_0001", "id_0000")

        table = self._get_table("Bloco 0", "0035", "id_0001", 1)
        self._save_table(filename, table, "0035", "id_0035", "id_0001")

        table = self._get_table("Bloco 0", "0100", "id_0001", 1)
        self._save_table(filename, table, "0100", "id_0100", "id_0001")

        table = self._get_table("Bloco 0", "0110")
        if table is not None:
            for _, row in table.iterrows():
                row = row.to_frame().T
                self._save_table(filename, row, "0110", "id_0110", "id_0001")

                sub_table = self._get_table("Bloco 0", "0111", "id_0110", row["id_0110"])
                self._save_table(filename, sub_table, "0111", "id_0111", "id_0110")

        table = self._get_table("Bloco 0", "0120", "id_0001", 1)
        self._save_table(filename, table, "0120", "id_0120", "id_0001")

        table = self._get_table("Bloco 0", "0140")
        if table is not None:
            for _, row in table.iterrows():
                row = row.to_frame().T
                self._save_table(filename, row, "0140", "id_0140", "id_0001")

                sub_table = self._get_table("Bloco 0", "0145", "id_0140", row["id_0140"])
                self._save_table(filename, sub_table, "0145", "id_0145", "id_0140")

                sub_table = self._get_table("Bloco 0", "0150", "id_0140", row["id_0140"])
                self._save_table(filename, sub_table, "0150", "id_0150", "id_0140")

                sub_table = self._get_table("Bloco 0", "0190", "id_0140", row["id_0140"])
                self._save_table(filename, sub_table, "0190", "id_0190", "id_0140")

                sub_table = self._get_table("Bloco 0", "0200", "id_0140", row["id_0140"])
                if sub_table is not None:
                    for _, sub_row in sub_table.iterrows():
                        sub_row = sub_row.to_frame().T
                        self._save_table(filename, sub_row, "0200", "id_0200", "id_0140")

                        sub_sub_table = self._get_table("Bloco 0", "0205", "id_0200", sub_row["id_0200"])
                        self._save_table(filename, sub_sub_table, "0205", "id_0205", "id_0200")

                        sub_sub_table = self._get_table("Bloco 0", "0206", "id_0200", sub_row["id_0200"])
                        self._save_table(filename, sub_sub_table, "0206", "id_0206", "id_0200")

                        sub_sub_table = self._get_table("Bloco 0", "0208", "id_0200", sub_row["id_0200"])
                        self._save_table(filename, sub_sub_table, "0208", "id_0208", "id_0200")

                sub_table = self._get_table("Bloco 0", "0400", "id_0140", row["id_0140"])
                if sub_table is not None:
                    for _, sub_row in sub_table.iterrows():
                        sub_row = sub_row.to_frame().T
                        self._save_table(filename, sub_row, "0400", "id_0400", "id_0140")

                zero450 = self._get_table("Bloco 0", "0450", "id_0140", row["id_0140"])
                self._save_table(filename, zero450, "0450", "id_0450", "id_0140")

        table = self._get_table("Bloco 0", "0500", "id_0001", 1)
        self._save_table(filename, table, "0500", "id_0500", "id_0001")

        table = self._get_table("Bloco 0", "0600", "id_0001", 1)
        self._save_table(filename, table, "0600", "id_0600", "id_0001")

        table = self._get_table("Bloco 0", "0900", "id_0001", 1)
        self._save_table(filename, table, "0900", "id_0900", "id_0001")

        table = self._get_table("Bloco 0", "0990", "id_0000", 1)
        self._save_table(filename, table, "0990", "id_0990", "id_0000")

        # Start of block A.
        table = self._get_table("Bloco A", "A001")
        self._save_table(filename, table, "A001", "id_A001")

        table = self._get_table("Bloco A", "A010", "id_A001", 1)
        self._save_table(filename, table, "A010", "id_A010", "id_A001")

        table = self._get_table("Bloco A", "A100")
        if table is not None:
            for _, row in table.iterrows():
                row = row.to_frame().T
                self._save_table(filename, row, "A100", "id_A100", "id_A010")

                table = self._get_table("Bloco A", "A110", "id_A100", row["id_A100"])
                self._save_table(filename, table, "A110", "id_A110", "id_A100")

                table = self._get_table("Bloco A", "A111", "id_A100", row["id_A100"])
                self._save_table(filename, table, "A111", "id_A111", "id_A100")

                table = self._get_table("Bloco A", "A120", "id_A100", row["id_A100"])
                self._save_table(filename, table, "A120", "id_A120", "id_A100")

                table = self._get_table("Bloco A", "A170", "id_A100", row["id_A100"])
                self._save_table(filename, table, "A170", "id_A170", "id_A100")

        table = self._get_table("Bloco A", "A990", "id_A001", 1)
        self._save_table(filename, table, "A990", "id_A990", "id_A001")

        # Start of block C.
        c001 = self._get_table("Bloco C", "C001")
        self._save_table(filename, c001, "C001", "id_c001")

        c010 = self._get_table("Bloco C", "C010")
        if c010 is not None:
            for _, c010_row in c010.iterrows():
                c010_row = c010_row.to_frame().T
                self._save_table(filename, c010_row, "C010", "id_c010", "id_c001")

                c100 = self._get_table("Bloco C", "C100", "id_c010", c010_row["id_c010"])
                if c100 is not None:
                    for _, c100_row in c100.iterrows():
                        c100_row = c100_row.to_frame().T
                        self._save_table(filename, c100_row, "C100", "id_c100", "id_c010")

                        c110 = self._get_table("Bloco C", "C110", "id_c100", c100_row["id_c100"])
                        self._save_table(filename, c110, "C110", "id_c110", "id_c100")

                        c111 = self._get_table("Bloco C", "C111", "id_c100", c100_row["id_c100"])
                        self._save_table(filename, c111, "C111", "id_c111", "id_c100")

                        c120 = self._get_table("Bloco C", "C120", "id_c100", c100_row["id_c100"])
                        self._save_table(filename, c120, "C120", "id_c120", "id_c100")

                        c170 = self._get_table("Bloco C", "C170", "id_c100", c100_row["id_c100"])
                        self._save_table(filename, c170, "C170", "id_c170", "id_c100")

                        c175 = self._get_table("Bloco C", "C175", "id_c100", c100_row["id_c100"])
                        self._save_table(filename, c175, "C175", "id_c175", "id_c100")

                        c180 = self._get_table("Bloco C", "C180", "id_c100", c100_row["id_c100"])
                        if c180 is not None:
                            for _, c180_row in c180.iterrows():
                                c180_row = c180_row.to_frame().T
                                self._save_table(filename, c180_row, "C180", "id_c180", "id_c010")

                                c181 = self._get_table("Bloco C", "C181", "id_c180", c180_row["id_c180"])
                                self._save_table(filename, c181, "C181", "id_c181", "id_c180")

                                c185 = self._get_table("Bloco C", "C185", "id_c180", c180_row["id_c180"])
                                self._save_table(filename, c185, "C185", "id_c185", "id_c180")

                                c188 = self._get_table("Bloco C", "C188", "id_c180", c180_row["id_c180"])
                                self._save_table(filename, c188, "C188", "id_c188", "id_c180")

                        c190 = self._get_table("Bloco C", "C190", "id_c100", c100_row["id_c100"])
                        if c190 is not None:
                            for _, c190_row in c190.iterrows():
                                c190_row = c190_row.to_frame().T
                                self._save_table(filename, c190_row, "C190", "id_c190", "id_c010")

                                c191 = self._get_table("Bloco C", "C191", "id_c190", c190_row["id_c190"])
                                self._save_table(filename, c191, "C191", "id_c191", "id_c190")

                                c195 = self._get_table("Bloco C", "C195", "id_c190", c190_row["id_c190"])
                                self._save_table(filename, c195, "C195", "id_c195", "id_c190")

                                c198 = self._get_table("Bloco C", "C198", "id_c190", c190_row["id_c190"])
                                self._save_table(filename, c198, "C198", "id_c198", "id_c190")

                                c199 = self._get_table("Bloco C", "C199", "id_c190", c190_row["id_c190"])
                                self._save_table(filename, c199, "C199", "id_c199", "id_c190")

                        c380 = self._get_table("Bloco C", "C380", "id_c100", c100_row["id_c100"])
                        if c380 is not None:
                            for _, c380_row in c380.iterrows():
                                c380_row = c380_row.to_frame().T
                                self._save_table(filename, c380_row, "C380", "id_c380", "id_c010")

                                c381 = self._get_table("Bloco C", "C381", "id_c380", c380_row["id_c380"])
                                self._save_table(filename, c381, "C381", "id_c381", "id_c380")

                                c385 = self._get_table("Bloco C", "C385", "id_c380", c380_row["id_c380"])
                                self._save_table(filename, c385, "C385", "id_c385", "id_c380")

                        c395 = self._get_table("Bloco C", "C395", "id_c100", c100_row["id_c100"])
                        if c395 is not None:
                            for _, c395_row in c395.iterrows():
                                c395_row = c395_row.to_frame().T
                                self._save_table(filename, c395_row, "C395", "id_c395", "id_c010")

                                c396 = self._get_table("Bloco C", "C396", "id_c395", c395_row["id_c395"])
                                self._save_table(filename, c396, "C396", "id_c396", "id_c395")

                        c400 = self._get_table("Bloco C", "C400", "id_c100", c100_row["id_c100"])
                        if c400 is not None:
                            for _, c400_row in c400.iterrows():
                                c400_row = c400_row.to_frame().T
                                self._save_table(filename, c400_row, "C400", "id_c400", "id_c100")

                                c405 = self._get_table("Bloco C", "C405", "id_c400", c400_row["id_c400"])
                                if c405 is not None:
                                    for _, c405_row in c405.iterrows():
                                        c405_row = c405_row.to_frame().T
                                        self._save_table(filename, c405_row, "C405", "id_c405", "id_c400")

                                        c481 = self._get_table("Bloco C", "C481", "id_c405", c405_row["id_c405"])
                                        self._save_table(filename, c481, "C481", "id_c481", "id_c405")

                                        c485 = self._get_table("Bloco C", "C485", "id_c405", c405_row["id_c405"])
                                        self._save_table(filename, c485, "C485", "id_c485", "id_c405")

                                c489 = self._get_table("Bloco C", "C489", "id_c400", c400_row["id_c400"])
                                self._save_table(filename, c489, "C489", "id_c489", "id_c400")

                                c490 = self._get_table("Bloco C", "C490", "id_c400", c400_row["id_c400"])
                                if c490 is not None:
                                    for _, c490_row in c490.iterrows():
                                        c490_row = c490_row.to_frame().T
                                        self._save_table(filename, c490_row, "C490", "id_c490", "id_c010")

                                        c491 = self._get_table("Bloco C", "C491", "id_c490", c490_row["id_c490"])
                                        self._save_table(filename, c491, "C491", "id_c491", "id_c490")

                                        c495 = self._get_table("Bloco C", "C495", "id_c490", c490_row["id_c490"])
                                        self._save_table(filename, c495, "C495", "id_c495", "id_c490")

                                        c499 = self._get_table("Bloco C", "C499", "id_c490", c490_row["id_c490"])
                                        self._save_table(filename, c499, "C499", "id_c499", "id_c490")

                        c500 = self._get_table("Bloco C", "C500", "id_c100", c100_row["id_c100"])
                        if c500 is not None:
                            for _, c500_row in c500.iterrows():
                                c500_row = c500_row.to_frame().T
                                self._save_table(filename, c500_row, "C500", "id_c500", "id_c100")

                                c501 = self._get_table("Bloco C", "C501", "id_c500", c500_row["id_c500"])
                                self._save_table(filename, c501, "C501", "id_c501", "id_c500")

                                c505 = self._get_table("Bloco C", "C505", "id_c500", c500_row["id_c500"])
                                self._save_table(filename, c505, "C505", "id_c505", "id_c500")

                                c509 = self._get_table("Bloco C", "C509", "id_c500", c500_row["id_c500"])
                                self._save_table(filename, c509, "C509", "id_c509", "id_c500")

                        c600 = self._get_table("Bloco C", "C600", "id_c100", c100_row["id_c100"])
                        if c600 is not None:
                            for _, c600_row in c600.iterrows():
                                c600_row = c600_row.to_frame().T
                                self._save_table(filename, c600_row, "C600", "id_c600")

                                c601 = self._get_table("Bloco C", "C601", "id_c600", c600_row["id_c600"])
                                self._save_table(filename, c601, "C601", "id_c601", "id_c600")

                                c605 = self._get_table("Bloco C", "C605", "id_c600", c600_row["id_c600"])
                                self._save_table(filename, c605, "C605", "id_c605", "id_c600")

                                c609 = self._get_table("Bloco C", "C609", "id_c600", c600_row["id_c600"])
                                self._save_table(filename, c609, "C609", "id_c609", "id_c600")

                        c860 = self._get_table("Bloco C", "C860", "id_c100", c100_row["id_c100"])
                        if c860 is not None:
                            for _, c860_row in c860.iterrows():
                                c860_row = c860_row.to_frame().T
                                self._save_table(filename, c860_row, "C860", "id_c860", "id_c100")

                                c870 = self._get_table("Bloco C", "C870", "id_c860", c860_row["id_c860"])
                                self._save_table(filename, c870, "C870", "id_c870", "id_c860")

                                c880 = self._get_table("Bloco C", "C880", "id_c860", c860_row["id_c860"])
                                self._save_table(filename, c880, "C880", "id_c860", "id_c860")

                                c890 = self._get_table("Bloco C", "C890", "id_c860", c860_row["id_c860"])
                                self._save_table(filename, c890, "C890", "id_c890", "id_c860")

        table = self._get_table("Bloco C", "C990", "id_c990", 1)
        self._save_table(filename, table, "C990", "id_c990", "id_c001")

        # Start of block D.
        d001 = self._get_table("Bloco D", "D001")
        self._save_table(filename, d001, "D001", "id_D001")

        d010 = self._get_table("Bloco D", "D010", "id_D001", d001["id_D001"])
        self._save_table(filename, d010, "D010", "id_D010", "id_D001")

        d100 = self._get_table("Bloco D", "D100", "id_D001", d001["id_D001"])
        if d100 is not None:
            for _, d100_row in d100.iterrows():
                d100_row = d100_row.to_frame().T
                self._save_table(filename, d100_row, "D100", "id_D100", "id_D001")

                d101 = self._get_table("Bloco D", "D101", "id_D100", d100_row["id_D100"])
                self._save_table(filename, d101, "D101", "id_D101", "id_D100")

                d105 = self._get_table("Bloco D", "D105", "id_D100", d100_row["id_D100"])
                self._save_table(filename, d105, "D105", "id_D105", "id_D100")

                d111 = self._get_table("Bloco D", "D111", "id_D100", d100_row["id_D100"])
                self._save_table(filename, d111, "D111", "id_D111", "id_D100")

        d200 = self._get_table("Bloco D", "D200", "id_D001", d001["id_D001"])
        if d200 is not None:
            for _, d200_row in d200.iterrows():
                d200_row = d200_row.to_frame().T
                self._save_table(filename, d200_row, "D200", "id_D200", "id_D001")

                d201 = self._get_table("Bloco D", "D201", "id_D200", d200_row["id_D200"])
                self._save_table(filename, d201, "D201", "id_D201", "id_D200")

                d205 = self._get_table("Bloco D", "D205", "id_D200", d200_row["id_D200"])
                self._save_table(filename, d205, "D205", "id_D205", "id_D200")

                d209 = self._get_table("Bloco D", "D209", "id_D200", d200_row["id_D200"])
                self._save_table(filename, d209, "D209", "id_D209", "id_D200")

        d300 = self._get_table("Bloco D", "D300", "id_D001", d001["id_D001"])
        if d300 is not None:
            for _, d300_row in d300.iterrows():
                d300_row = d300_row.to_frame().T
                self._save_table(filename, d300_row, "D300", "id_D300", "id_D001")

                d309 = self._get_table("Bloco D", "D309", "id_D300", d300_row["id_D300"])
                self._save_table(filename, d309, "D309", "id_D309", "id_D300")

        d350 = self._get_table("Bloco D", "D350", "id_D001", d001["id_D001"])
        if d350 is not None:
            for _, d350_row in d350.iterrows():
                d350_row = d350_row.to_frame().T
                self._save_table(filename, d350_row, "D350", "id_D350", "id_D001")

                d359 = self._get_table("Bloco D", "D359", "id_D350", d350_row["id_D350"])
                self._save_table(filename, d359, "D359", "id_D359", "id_D350")

        d500 = self._get_table("Bloco D", "D500", "id_D001", d001["id_D001"])
        if d500 is not None:
            for _, d500_row in d500.iterrows():
                d500_row = d500_row.to_frame().T
                self._save_table(filename, d500_row, "D500", "id_D500", "id_D001")

                d501 = self._get_table("Bloco D", "D501", "id_D500", d500_row["id_D500"])
                self._save_table(filename, d501, "D501", "id_D501", "id_D500")

                d505 = self._get_table("Bloco D", "D505", "id_D500", d500_row["id_D500"])
                self._save_table(filename, d505, "D505", "id_D505", "id_D500")

                d509 = self._get_table("Bloco D", "D509", "id_D500", d500_row["id_D500"])
                self._save_table(filename, d509, "D509", "id_D509", "id_D500")

        d600 = self._get_table("Bloco D", "D600", "id_D001", d001["id_D001"])
        if d600 is not None:
            for _, d600_row in d600.iterrows():
                d600_row = d600_row.to_frame().T
                self._save_table(filename, d600_row, "D600", "id_D600", "id_D001")

                d601 = self._get_table("Bloco D", "D601", "id_D600", d600_row["id_D600"])
                self._save_table(filename, d601, "D601", "id_D601", "id_D600")

                d605 = self._get_table("Bloco D", "D605", "id_D600", d600_row["id_D600"])
                self._save_table(filename, d605, "D605", "id_D605", "id_D600")

                d609 = self._get_table("Bloco D", "D609", "id_D600", d600_row["id_D600"])
                self._save_table(filename, d609, "D609", "id_D609", "id_D600")

        d990 = self._get_table("Bloco D", "D990", "id_D001", d001["id_D001"])
        self._save_table(filename, d990, "D990", "id_D990", "id_D001")

        # Start of block F.
        f001 = self._get_table("Bloco F", "F001")
        self._save_table(filename, f001, "F001", "id_F001")

        f010 = self._get_table("Bloco F", "F010", "id_F001", f001["id_F001"])
        if f010 is not None:
            for _, f010_row in f010.iterrows():
                f010_row = f010_row.to_frame().T
                self._save_table(filename, f010_row, "F010", "id_F010", "id_F001")

                f100 = self._get_table("Bloco F", "F100", "id_F010", f010_row["id_F010"])
                if f100 is not None:
                    for _, f100_row in f100.iterrows():
                        f100_row = f100_row.to_frame().T
                        self._save_table(filename, f100_row, "F100", "id_F100", "id_F010")

                        f111 = self._get_table("Bloco F", "F111", "id_F100", f100_row["id_F100"])
                        self._save_table(filename, f111, "F111", "id_F111", "id_F100")

                f120 = self._get_table("Bloco F", "F120", "id_F010", "id_F010")
                if f120 is not None:
                    for _, f120_row in f120.iterrows():
                        f120_row = f120_row.to_frame().T
                        self._save_table(filename, f120_row, "F120", "id_F120", "id_F010")

                        f129 = self._get_table("Bloco F", "F129", "id_F120", f120_row["id_F120"])
                        self._save_table(filename, f129, "F129", "id_F129", "id_F120")

                f130 = self._get_table("Bloco F", "F130", "id_F010", f010_row["id_F010"])
                if f130 is not None:
                    for _, f130_row in f130.iterrows():
                        f130_row = f130_row.to_frame().T
                        self._save_table(filename, f130_row, "F130", "id_F130", "id_F010")

                        f139 = self._get_table("Bloco F", "F139", "id_F130", f130_row["id_F130"])
                        self._save_table(filename, f139, "F139", "id_F139", "id_F130")

                f150 = self._get_table("Bloco F", "F150", "id_F010", f010_row["id_F010"])
                self._save_table(filename, f150, "F150", "id_F150", "id_F010")

                f200 = self._get_table("Bloco F", "F200", "id_F010", f010_row["id_F010"])
                if f200 is not None:
                    for _, f200_row in f200.iterrows():
                        f200_row = f200_row.to_frame().T
                        self._save_table(filename, f200_row, "F200", "id_F200", "id_F010")

                        f205 = self._get_table("Bloco F", "F205", "id_F200", f200_row["id_F200"])
                        self._save_table(filename, f205, "F205", "id_F205", "id_F200")

                        f210 = self._get_table("Bloco F", "F210", "id_F200", f200_row["id_F200"])
                        self._save_table(filename, f210, "F210", "id_F210", "id_F200")

                        f211 = self._get_table("Bloco F", "F211", "id_F200", f200_row["id_F200"])
                        self._save_table(filename, f211, "F211", "id_F211", "id_F200")

                f500 = self._get_table("Bloco F", "F500", "id_F010", f010_row["id_F010"])
                if f500 is not None:
                    for _, f500_row in f500.iterrows():
                        f500_row = f500_row.to_frame().T
                        self._save_table(filename, f500_row, "F500", "id_F500", "id_F010")

                        f509 = self._get_table("Bloco F", "F509", "id_F500", f500_row["id_F500"])
                        self._save_table(filename, f509, "F509", "id_F509", "id_F500")

                        f510 = self._get_table("Bloco F", "F510", "id_F500", f500_row["id_F500"])
                        self._save_table(filename, f510, "F510", "id_F510", "id_F500")

                        f519 = self._get_table("Bloco F", "F519", "id_F500", f500_row["id_F500"])
                        self._save_table(filename, f519, "F519", "id_F519", "id_F500")

                f525 = self._get_table("Bloco F", "F525", "id_F010", f010_row["id_F010"])
                self._save_table(filename, f525, "F525", "id_F525", "id_F010")

                f550 = self._get_table("Bloco F", "F550", "id_F010", f010_row["id_F010"])
                if f550 is not None:
                    for _, f550_row in f550.iterrows():
                        f550_row = f550_row.to_frame().T
                        self._save_table(filename, f550_row, "F550", "id_F550", "id_F010")

                        f559 = self._get_table("Bloco F", "F559", "id_F550", f550_row["id_F550"])
                        self._save_table(filename, f559, "F559", "id_F559", "id_F550")

                f560 = self._get_table("Bloco F", "F560", "id_F010", f010_row["id_F010"])
                if f560 is not None:
                    for _, f560_row in f560.iterrows():
                        f560_row = f560_row.to_frame().T
                        self._save_table(filename, f560_row, "F560", "id_F560", "id_F010")

                        f569 = self._get_table("Bloco F", "F569", "id_F560", f560_row["id_F560"])
                        self._save_table(filename, f569, "F569", "id_F569", "id_F560")

                f600 = self._get_table("Bloco F", "F600", "id_F010", f010_row["id_F010"])
                self._save_table(filename, f600, "F600", "id_F600", "id_F010")

                f700 = self._get_table("Bloco F", "F700", "id_F010", f010_row["id_F010"])
                self._save_table(filename, f700, "F700", "id_F700", "id_F010")

                f800 = self._get_table("Bloco F", "F800", "id_F010", f010_row["id_F010"])
                self._save_table(filename, f800, "F800", "id_F800", "id_F010")

        f990 = self._get_table("Bloco F", "F990", "id_F001", f001["id_F001"])
        self._save_table(filename, f990, "F990", "id_F990", "id_F001")

        # Start of block I.
        i001 = self._get_table("Bloco I", "I001")
        self._save_table(filename, i001, "I001", "id_I001")

        i010 = self._get_table("Bloco I", "I010", "id_I001", i001["id_I001"])
        if i010 is not None:
            for _, i010_row in i010.iterrows():
                i010_row = i010_row.to_frame().T
                self._save_table(filename, i010_row, "I010", "id_I010", "id_I001")

                i100 = self._get_table("Bloco I", "I100", "id_I010", i010["id_I010"])
                if i100 is not None:
                    for _, i100_row in i100.iterrows():
                        i100_row = i100_row.to_frame().T
                        self._save_table(filename, i100_row, "I100", "id_I100", "id_I010")

                        i199 = self._get_table("Bloco I", "I199", "id_I100", i100_row["id_I100"])
                        self._save_table(filename, i199, "I199", "id_I199", "id_I100")

                        i200 = self._get_table("Bloco I", "I200", "id_I100", i100["id_I100"])
                        if i200 is not None:
                            for _, i200_row in i200.iterrows():
                                i200_row = i200_row.to_frame().T
                                self._save_table(filename, i200_row, "I200", "id_I200", "id_I100")

                                i299 = self._get_table("Bloco I", "I299", "id_I200", i200_row["id_I200"])
                                self._save_table(filename, i299, "I299", "id_I299", "id_I200")

        i300 = self._get_table("Bloco I", "I300", "id_I001", i001["id_I001"])
        if i300 is not None:
            for _, i300_row in i300.iterrows():
                i300_row = i300_row.to_frame().T
                self._save_table(filename, i300_row, "I300", "id_I300", "id_I001")

                i399 = self._get_table("Bloco I", "I399", "id_I300", i300_row["id_I300"])
                self._save_table(filename, i399, "I399", "id_I399", "id_I300")

        i990 = self._get_table("Bloco I", "I990", "id_I001", i001["id_I001"])
        self._save_table(filename, i990, "I990", "id_I990", "id_I001")

        # Start of block M.
        m001 = self._get_table("Bloco M", "M001")
        self._save_table(filename, m001, "M001", "id_M001")

        m100 = self._get_table("Bloco M", "M100", "id_M001", m001["id_M001"])
        if m100 is not None:
            for _, m100_row in m100.iterrows():
                m100_row = m100_row.to_frame().T
                self._save_table(filename, m100_row, "M100", "id_M100", "id_M001")

                m105 = self._get_table("Bloco M", "M105", "id_M100", m100_row["id_M100"])
                self._save_table(filename, m105, "M105", "id_M105", "id_M100")

                m110 = self._get_table("Bloco M", "M110", "id_M100", m100_row["id_M100"])
                if m110 is not None:
                    for _, m110_row in m110.iterrows():
                        m110_row = m110_row.to_frame().T
                        self._save_table(filename, m110_row, "M110", "id_M110", "id_M100")

                        m115 = self._get_table("Bloco M", "M115", "id_M110", m110_row["id_M110"])
                        self._save_table(filename, m115, "M115", "id_M115", "id_M110")

        m200 = self._get_table("Bloco M", "M200", "id_M001", m001["id_M001"])
        if m200 is not None:
            for _, m200_row in m200.iterrows():
                m200_row = m200_row.to_frame().T
                self._save_table(filename, m200_row, "M200", "id_M200", "id_M001")

                m205 = self._get_table("Bloco M", "M205", "id_M200", m200_row["id_M200"])
                self._save_table(filename, m205, "M205", "id_M205", "id_M200")

                m210 = self._get_table("Bloco M", "M210", "id_M200", m200_row["id_M200"])
                if m210 is not None:
                    for _, m210_row in m210.iterrows():
                        m210_row = m210_row.to_frame().T
                        self._save_table(filename, m210_row, "M210", "id_M210", "id_M200")

                        m211 = self._get_table("Bloco M", "M211", "id_M210", m210_row["id_M210"])
                        self._save_table(filename, m211, "M211", "id_M211", "id_M210")

                        m215 = self._get_table("Bloco M", "M215", "id_M210", m210_row["id_M210"])
                        self._save_table(filename, m215, "M215", "id_M215", "id_M210")

                m220 = self._get_table("Bloco M", "M220", "id_M200", m200_row["id_M200"])
                if m220 is not None:
                    for _, m220_row in m220.iterrows():
                        m220_row = m220_row.to_frame().T
                        self._save_table(filename, m220_row, "M220", "id_M220", "id_M200")

                        m225 = self._get_table("Bloco M", "M225", "id_M220", m220_row["id_M220"])
                        self._save_table(filename, m225, "M225", "id_M225", "id_M220")

                m230 = self._get_table("Bloco M", "M230", "id_M200", m200_row["id_M200"])
                self._save_table(filename, m230, "M230", "id_M230", "id_M200")

        m300 = self._get_table("Bloco M", "M300", "id_M001", m001["id_M001"])
        self._save_table(filename, m300, "M300", "id_M300", "id_M001")

        m350 = self._get_table("Bloco M", "M350", "id_M001", m001["id_M001"])
        self._save_table(filename, m350, "M350", "id_M350", "id_M001")

        m400 = self._get_table("Bloco M", "M400", "id_M001", m001["id_M001"])
        if m400 is not None:
            for _, m400_row in m400.iterrows():
                m400_row = m400_row.to_frame().T
                self._save_table(filename, m400_row, "M400", "id_M400", "id_M001")

                m410 = self._get_table("Bloco M", "M410", "id_M400", m400_row["id_M400"])
                self._save_table(filename, m410, "M410", "id_M410", "id_M400")

        m500 = self._get_table("Bloco M", "M500", "id_M001", m001["id_M001"])
        if m500 is not None:
            for _, m500_row in m500.iterrows():
                m500_row = m500_row.to_frame().T
                self._save_table(filename, m500_row, "M500", "id_M500", "id_M001")

                m505 = self._get_table("Bloco M", "M505", "id_M500", m500_row["id_M500"])
                self._save_table(filename, m505, "M505", "id_M505", "id_M500")

                m510 = self._get_table("Bloco M", "M510", "id_M500", m500_row["id_M500"])
                if m510 is not None:
                    for _, m510_row in m510.iterrows():
                        m510_row = m510_row.to_frame().T
                        self._save_table(filename, m510_row, "M510", "id_M510", "id_M500")

                        m515 = self._get_table("Bloco M", "M515", "id_M510", m510_row["id_M510"])
                        self._save_table(filename, m515, "M515", "id_M515", "id_M510")

        m600 = self._get_table("Bloco M", "M600", "id_M001", m001["id_M001"])
        if m600 is not None:
            for _, m600_row in m600.iterrows():
                m600_row = m600_row.to_frame().T
                self._save_table(filename, m600_row, "M600", "id_M600", "id_M001")

                m605 = self._get_table("Bloco M", "M605", "id_M600", m600_row["id_M600"])
                self._save_table(filename, m605, "M605", "id_M605", "id_M600")

                m610 = self._get_table("Bloco M", "M610", "id_M600", m600_row["id_M600"])
                self._save_table(filename, m610, "M610", "id_M610", "id_M600")

                m611 = self._get_table("Bloco M", "M611", "id_M600", m600_row["id_M600"])
                self._save_table(filename, m611, "M611", "id_M611", "id_M600")

                m615 = self._get_table("Bloco M", "M615", "id_M600", m600_row["id_M600"])
                self._save_table(filename, m615, "M615", "id_M615", "id_M600")

                m620 = self._get_table("Bloco M", "M620", "id_M600", m600["id_M600"])
                if m620 is not None:
                    for _, m620_row in m620.iterrows():
                        m620_row = m620_row.to_frame().T
                        self._save_table(filename, m620_row, "M620", "id_M620", "id_M600")

                        m625 = self._get_table("Bloco M", "M625", "id_M620", m620_row["id_M620"])
                        self._save_table(filename, m625, "M625", "id_M625", "id_M620")

                m630 = self._get_table("Bloco M", "M630", "id_M600", m600_row["id_M600"])
                self._save_table(filename, m630, "M630", "id_M630", "id_M600")

        m700 = self._get_table("Bloco M", "M700", "id_M001", m001["id_M001"])
        self._save_table(filename, m700, "M700", "id_M700", "id_M001")

        m800 = self._get_table("Bloco M", "M800", "id_M001", m001["id_M001"])
        if m800 is not None:
            for _, m800_row in m800.iterrows():
                m800_row = m800_row.to_frame().T
                self._save_table(filename, m800_row, "M800", "id_M800", "id_M001")

                m810 = self._get_table("Bloco M", "M810", "id_M800", m800_row["id_M800"])
                self._save_table(filename, m810, "M810", "id_M810", "id_M800")

        m990 = self._get_table("Bloco M", "M990", "id_M001", m001["id_M001"])
        self._save_table(filename, m990, "M990", "id_M990", "id_M001")

        # Start of block P.
        p001 = self._get_table("Bloco P", "P001")
        self._save_table(filename, p001, "P001", "id_P001")

        p010 = self._get_table("Bloco P", "P010", "id_P001", p001["id_P001"])
        self._save_table(filename, p010, "P010", "id_P010", "id_P001")

        if p010 is not None:
            p100 = self._get_table("Bloco P", "P100", "id_P010", p010["id_P010"])
            if p100 is not None:
                for _, p100_row in p100.iterrows():
                    p100_row = p100_row.to_frame().T
                    self._save_table(filename, p100_row, "P100", "id_P100", "id_P010")

                    p110 = self._get_table("Bloco P", "P110", "id_P100", p100_row["id_P100"])
                    self._save_table(filename, p110, "P110", "id_P110", "id_P100")

                    p199 = self._get_table("Bloco P", "P199", "id_P100", p100_row["id_P100"])
                    self._save_table(filename, p199, "P199", "id_P199", "id_P100")

            p200 = self._get_table("Bloco P", "P200", "id_P010", p010["id_P010"])
            if p200 is not None:
                for _, p200_row in p200.iterrows():
                    p200_row = p200_row.to_frame().T
                    self._save_table(filename, p200_row, "P200", "id_P200", "id_P010")

                    p210 = self._get_table("Bloco P", "P210", "id_P200", p200_row["id_P200"])
                    self._save_table(filename, p210, "P210", "id_P210", "id_P200")

        p990 = self._get_table("Bloco P", "P990", "id_P001", p001["id_P001"])
        self._save_table(filename, p990, "P990", "id_P990", "id_P001")

        # Start of block 1.
        one001 = self._get_table("Bloco 1", "1001")
        self._save_table(filename, one001, "1001", "id_1001")

        one010 = self._get_table("Bloco 1", "1010", "id_1001", one001["id_1001"])
        if one010 is not None:
            for _, one010_row in one010.iterrows():
                one010_row = one010_row.to_frame().T
                self._save_table(filename, one010_row, "1010", "id_1010", "id_1001")

                one011 = self._get_table("Bloco 1", "1011", "id_1010", one010_row["id_1010"])
                self._save_table(filename, one011, "1011", "id_1011", "id_1010")

        one020 = self._get_table("Bloco 1", "1020", "id_1001", one001["id_1001"])
        self._save_table(filename, one020, "1020", "id_1020", "id_1001")

        one050 = self._get_table("Bloco 1", "1050", "id_1001", one001["id_1001"])
        self._save_table(filename, one050, "1050", "id_1050", "id_1001")

        one100 = self._get_table("Bloco 1", "1100", "id_1001", one001["id_1001"])
        if one100 is not None:
            for _, one100_row in one100.iterrows():
                one100_row = one100_row.to_frame().T
                self._save_table(filename, one100_row, "1100", "id_1100", "id_1001")

                one101 = self._get_table("Bloco 1", "1101", "id_1100", one100_row["id_1100"])
                self._save_table(filename, one101, "1101", "id_1101", "id_1100")

                one102 = self._get_table("Bloco 1", "1102", "id_1100", one100_row["id_1100"])
                self._save_table(filename, one102, "1102", "id_1102", "id_1100")

        one200 = self._get_table("Bloco 1", "1200", "id_1001", one001["id_1001"])
        if one200 is not None:
            for _, one200_row in one200.iterrows():
                one200_row = one200_row.to_frame().T
                self._save_table(filename, one200_row, "1200", "id_1200", "id_1001")

                one210 = self._get_table("Bloco 1", "1210", "id_1200", one200_row["id_1200"])
                self._save_table(filename, one210, "1210", "id_1210", "id_1200")

                one220 = self._get_table("Bloco 1", "1220", "id_1200", one200_row["id_1200"])
                self._save_table(filename, one220, "1220", "id_1220", "id_1200")

        one300 = self._get_table("Bloco 1", "1300", "id_1001", one001["id_1001"])
        self._save_table(filename, one300, "1300", "id_1300", "id_1001")

        one500 = self._get_table("Bloco 1", "1500", "id_1001", one001["id_1001"])
        if one500 is not None:
            for _, one500_row in one500.iterrows():
                one500_row = one500_row.to_frame().T
                self._save_table(filename, one500_row, "1500", "id_1500", "id_1001")

                one501 = self._get_table("Bloco 1", "1501", "id_1500", one500_row["id_1500"])
                self._save_table(filename, one501, "1501", "id_1501", "id_1500")

                one502 = self._get_table("Bloco 1", "1502", "id_1500", one500_row["id_1500"])
                self._save_table(filename, one502, "1502", "id_1502", "id_1500")

        one600 = self._get_table("Bloco 1", "1600", "id_1001", one001["id_1001"])
        if one600 is not None:
            for _, one600_row in one600.iterrows():
                one600_row = one600_row.to_frame().T
                self._save_table(filename, one600_row, "1600", "id_1600", "id_1001")

                one610 = self._get_table("Bloco 1", "1610", "id_1600", one600_row["id_1600"])
                self._save_table(filename, one610, "1610", "id_1610", "id_1600")

                one620 = self._get_table("Bloco 1", "1620", "id_1600", one600_row["id_1600"])
                self._save_table(filename, one620, "1620", "id_1620", "id_1600")

        one700 = self._get_table("Bloco 1", "1700", "id_1001", one001["id_1001"])
        self._save_table(filename, one700, "1700", "id_1700", "id_1001")

        one800 = self._get_table("Bloco 1", "1800", "id_1001", one001["id_1001"])
        if one800 is not None:
            for _, one800_row in one800.iterrows():
                one800_row = one800_row.to_frame().T
                self._save_table(filename, one800_row, "1800", "id_1800", "id_1001")

                one809 = self._get_table("Bloco 1", "1809", "id_1800", one800_row["id_1800"])
                self._save_table(filename, one809, "1809", "id_1809", "id_1600")

        one900 = self._get_table("Bloco 1", "1900", "id_1001", one001["id_1001"])
        self._save_table(filename, one900, "1900", "id_1900", "id_1001")

        one990 = self._get_table("Bloco 1", "1990", "id_1001", one001["id_1001"])
        self._save_table(filename, one990, "1990", "id_1990", "id_1001")

        # Start of block 9.
        nine001 = self._get_table("Bloco 9", "9001")
        self._save_table(filename, nine001, "9001", "id_9001")

        nine900 = self._get_table("Bloco 9", "9900", "id_9001", nine001["id_9001"])
        self._save_table(filename, nine900, "9900", "id_9900", "id_9001")

        nine990 = self._get_table("Bloco 9", "9990", "id_9001", nine001["id_9001"])
        self._save_table(filename, nine990, "9990", "id_9990", "id_9001")

        nine999 = self._get_table("Bloco 9", "9999")
        self._save_table(filename, nine999, "9999", "id_9999")

        # Append a | at the end of every line.
        with open(filename, 'r', encoding="utf-8") as fp:
            lines = fp.readlines()

        new_lines = [line.replace("\n", "|\n") for line in lines]

        with open(filename, 'w', encoding="utf-8") as fp:
            fp.writelines(new_lines)

    def __getitem__(self, name: str) -> Block:
        return self.blocks[name]

    def __repr__(self) -> str:
        return f"Sped(blocks={list(self.blocks.keys())})"
