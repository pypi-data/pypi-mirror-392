""" Reader for SPED files. """
from collections import defaultdict
import pandas as pd

from .sped import Block, Sped

class SpedReader:
    """ SpedReader class. """

    def __init__(self, file_path):
        self.file_path = file_path

    def parse_block_0(self, lines):
        """ Parse block 0 of a SPED file.
            Parameter:
            lines: list of strings.
            Returns a dictionary of DataFrame objects.
        """
        block_zero = defaultdict(list)

        ids = {'0000': None,
               '0001': None,
               '0035': None,
               '0100': None,
               '0110': None,
               '0111': None,
               '0120': None,
               '0140': None,
               '0145': None,
               '0150': None,
               '0190': None,
               '0200': None,
               '0205': None,
               '0206': None,
               '0208': None,
               '0400': None,
               '0450': None,
               '0500': None,
               '0600': None,
               '0900': None,
               '0990': None}

        for line in lines:
            parts = line.strip().split("|")

            # Prevents index error when a file is malformed.
            if len(parts) < 2:
                continue

            registry = parts[1]

            if registry == "0000":
                ids["0000"] = len(block_zero["0000"]) + 1
                block_zero["0000"].append({"id_0000": ids["0000"], "cod_ver": parts[2],
                                        "tipo_escrit": parts[3], "ind_sit_esp": parts[4],
                                        "num_rec_anterior": parts[5], "dt_ini": parts[6],
                                        "dt_fin": parts[7], "nome": parts[8], "cnpj": parts[9],
                                        "uf": parts[10], "cod_mun": parts[11], "suframa": parts[12],
                                        "ind_nat_pj": parts[13], "ind_ativ": parts[14]})
            elif registry == "0001" and ids["0000"]:
                ids["0001"] = len(block_zero["0001"]) + 1
                block_zero["0001"].append({"id_0001": ids["0001"], "id_0000": ids["0000"],
                                         "ind_mov": parts[2]})
            elif registry == "0035" and ids["0001"]:
                ids["0035"] = len(block_zero["0035"]) + 1
                block_zero["0035"].append({"id_0035": ids["0035"], "id_0001": ids["0001"],
                                         "cod_scp": parts[2], "desc_scp": parts[3],
                                         "inf_comp": parts[4]})
            elif registry == "0100" and ids["0001"]:
                ids["0100"] = len(block_zero["0100"]) + 1
                block_zero["0100"].append({"id_0100": ids["0100"], "id_0001": ids["0001"],
                                        "nome": parts[2], "cpf": parts[3], "crc": parts[4],
                                        "cnpj": parts[5], "cep": parts[6], "end": parts[7],
                                        "num": parts[8], "compl": parts[9], "bairro": parts[10],
                                        "fone": parts[11], "fax": parts[12], "email": parts[13],
                                        "cod_num": parts[14]})
            elif registry == "0110" and ids["0001"]:
                ids["0110"] = len(block_zero["0110"]) + 1
                block_zero["0110"].append({"id_0110": ids["0110"], "id_0001": ids["0001"],
                                        "cod_inc_trib": parts[2], "ind_apro_cred": parts[3],
                                        "cod_tipo_cont": parts[4], "ind_reg_cum": parts[5]})
            elif registry == "0111" and ids["0110"]:
                ids["0111"] = len(block_zero["0111"]) + 1
                block_zero["0111"].append({"id_0111": ids["0111"], "id_0110": ids["0110"],
                                        "rec_bru_ncum_trib": parts[2], "rec_bru_ncum_nt_mi": parts[3],
                                        "rec_bru_ncum_exp": parts[4], "rec_bru_cum": parts[5],
                                        "rec_bru_total": parts[6]})
            elif registry == "0120" and ids["0001"]:
                ids["0120"] = len(block_zero["0120"]) + 1
                block_zero["0120"].append({"id_0120": ids["0120"], "id_0001": ids["0001"],
                                        "mes_refer": parts[2], "inf_comp": parts[3]})
            elif registry == "0140" and ids["0001"]:
                ids["0140"] = len(block_zero["0140"]) + 1
                block_zero["0140"].append({"id_0140": ids["0140"], "id_0001": ids["0001"],
                                        "cod_est": parts[2], "nome": parts[3], "cnpj": parts[4],
                                        "uf": parts[5], "ie": parts[6], "cod_mun": parts[7],
                                        "im": parts[8], "suframa": parts[9]})
            elif registry == "0145" and ids["0140"]:
                ids["0145"] = len(block_zero["0145"]) + 1
                block_zero["0145"].append({"id_0145": ids["0145"], "id_0140": ids["0140"],
                                        "cod_inc_trib": parts[2], "vl_rec_tot": parts[3],
                                        "vl_rec_ativ": parts[4], "vl_rec_demis_ativ": parts[5],
                                        "info_compl": parts[6]})
            elif registry == "0150" and ids["0140"]:
                ids["0150"] = len(block_zero["0150"]) + 1
                block_zero["0150"].append({"id_0150": ids["0150"], "id_0140": ids["0140"],
                                        "cod_part": parts[2], "nome": parts[3], "cod_pais": parts[4],
                                        "cnpj": parts[5], "cpf": parts[6], "ie": parts[7],
                                        "cod_mun": parts[8], "suframa": parts[9], "end": parts[10],
                                        "num": parts[11], "compl": parts[12], "bairro": parts[13]})
            elif registry == "0190" and ids["0140"]:
                ids["0190"] = len(block_zero["0190"]) + 1
                block_zero["0190"].append({"id_0190": ids["0190"], "id_0140": ids["0140"],
                                        "unid": parts[2], "descr": parts[3]})
            elif registry == "0200" and ids["0140"]:
                ids["0200"] = len(block_zero["0200"]) + 1
                block_zero["0200"].append({"id_0200": ids["0200"], "id_0140": ids["0140"],
                                        "cod_item": parts[2], "descr_item": parts[3],
                                        "cod_barra": parts[4], "cod_ant_item": parts[5],
                                        "unid_inv": parts[6], "tipo_item": parts[7],
                                        "cod_ncm": parts[8], "ex_ipi": parts[9],
                                        "cod_gen": parts[10], "cod_lst": parts[11],
                                        "aliq_icms": parts[12]})
            elif registry == "0205" and ids["0200"]:
                ids["0205"] = len(block_zero["0205"]) + 1
                block_zero["0205"].append({"id_0205": ids["0205"], "id_0200": ids["0200"],
                                        "descr_ant_item": parts[2], "dt_ini": parts[3],
                                        "dt_fim": parts[4], "cod_ant_item": parts[5]})
            elif registry == "0206" and ids["0200"]:
                ids["0206"] = len(block_zero["0206"]) + 1
                block_zero["0206"].append({"id_0206": ids["0206"], "id_0200": ids["0200"],
                                        "cod_comb": parts[2]})
            elif registry == "0208" and ids["0200"]:
                ids["0208"] = len(block_zero["0208"]) + 1
                block_zero["0208"].append({"id_0208": ids["0208"], "id_0200": ids["0200"],
                                        "cod_tab": parts[2], "cod_gru": parts[3],
                                        "marca_com": parts[4]})
            elif registry == "0400" and ids["0140"]:
                ids["0400"] = len(block_zero["0400"]) + 1
                block_zero["0400"].append({"id_0400": ids["0400"], "id_0140": ids["0140"],
                                        "cod_nat": parts[2], "descr_nat": parts[3]})
            elif registry == "0450" and ids["0140"]:
                ids["0450"] = len(block_zero["0450"]) + 1
                block_zero["0450"].append({"id_0450": ids["0450"], "id_0140": ids["0140"],
                                        "cod_inf": parts[2], "txt": parts[3]})
            elif registry == "0500" and ids["0001"]:
                ids["0500"] = len(block_zero["0500"]) + 1
                block_zero["0500"].append({"id_0500": ids["0500"], "id_0001": ids["0001"],
                                        "dt_alt": parts[2], "cod_nat_cc": parts[3],
                                        "ind_cta": parts[4], "nivel": parts[5],
                                        "cod_cta": parts[6], "nome_cta": parts[7],
                                        "cod_cta_ref": parts[8], "cnpj_est": parts[9]})
            elif registry == "0600" and ids["0001"]:
                ids["0600"] = len(block_zero["0600"]) + 1
                block_zero["0600"].append({"id_0600": ids["0600"], "id_0001": ids["0001"],
                                        "dt_alt": parts[2], "cod_ccus": parts[3],
                                        "ccus": parts[4]})
            elif registry == "0900" and ids["0001"]:
                ids["0900"] = len(block_zero["0900"]) + 1
                block_zero["0900"].append({"id_0900": ids["0900"], "id_0001": ids["0001"],
                                        "rec_total_bloco_a": parts[2], "rec_nrb_bloco_a": parts[3],
                                        "rec_total_bloco_c": parts[4], "rec_nrb_bloco_c": parts[5],
                                        "rec_total_bloco_d": parts[6], "rec_nrb_bloco_d": parts[7],
                                        "rec_total_bloco_f": parts[8], "rec_nrb_bloco_f": parts[9],
                                        "rec_total_bloco_i": parts[10], "rec_nrb_bloco_i": parts[11],
                                        "rec_total_bloco_1": parts[12], "rec_nrb_bloco_1": parts[13],
                                        "rec_total_periodo": parts[14], "rec_total_nrb_periodo": parts[15]})
            elif registry == "0990" and ids["0000"]:
                ids["0990"] = len(block_zero["0990"]) + 1
                block_zero["0990"].append({"id_0990": ids["0990"], "id_0000": ids["0000"], "qtd_lin_0": parts[2]})

        return {reg: pd.DataFrame(table) for reg, table in block_zero.items()}

    def parse_block_a(self, lines):
        """ Parse block A of a SPED file.
            Parameter:
            lines: list of strings.
            Returns a dictionary of DataFrame objects.
        """
        block_a = defaultdict(list)

        ids = {'A001': None,
               'A010': None,
               'A100': None,
               'A110': None,
               'A111': None,
               'A120': None,
               'A170': None,
               'A990': None}

        for line in lines:
            parts = line.strip().split("|")

            # Prevents index error when a file is malformed.
            if len(parts) < 2:
                continue

            registry = parts[1]

            if registry == "A001":
                ids["A001"] = len(block_a["A001"]) + 1
                block_a["A001"].append({"id_A001": ids["A001"], "ind_mov": parts[2]})
            elif registry == "A010" and ids["A001"]:
                ids["A010"] = len(block_a["A010"]) + 1
                block_a["A010"].append({"id_A010": ids["A010"], "id_A001": ids["A001"],
                                        "cnpj": parts[2]})
            elif registry == "A100" and ids["A001"]:
                ids["A100"] = len(block_a["A100"]) + 1
                block_a["A100"].append({"id_A100": ids["A100"], "id_A001": ids["A001"],
                                        "ind_oper": parts[2], "ind_emit": parts[3],
                                        "cod_part": parts[4], "cod_sit": parts[5],
                                        "ser": parts[6], "sub": parts[7],
                                        "num_doc": parts[8], "chv_nfse": parts[9],
                                        "dt_doc": parts[10], "dt_exe_serv": parts[11],
                                        "vl_doc": parts[12], "ind_pgto": parts[13],
                                        "vl_desc": parts[14], "vl_bc_pis": parts[15],
                                        "vl_pis": parts[16], "vl_bc_cofins": parts[17],
                                        "vl_cofins": parts[18], "vl_pis_ret": parts[19],
                                        "vl_cofins_ret": parts[20], "vl_iss": parts[21]})
            elif registry == "A110" and ids["A100"]:
                ids["A110"] = len(block_a["A110"]) + 1
                block_a["A110"].append({"id_A110": ids["A110"], "id_A100": ids["A100"],
                                        "cod_ind": parts[2], "txt_compl": parts[3]})
            elif registry == "A111" and ids["A100"]:
                ids["A111"] = len(block_a["A111"]) + 1
                block_a["A111"].append({"id_A111": ids["A111"], "id_A100": ids["A100"],
                                        "num_proc": parts[2], "ind_proc": parts[3]})
            elif registry == "A120" and ids["A100"]:
                ids["A120"] = len(block_a["A120"]) + 1
                block_a["A120"].append({"id_A120": ids["A120"], "id_A100": ids["A100"],
                                        "vl_tot_serv": parts[2], "vl_bc_pis": parts[3],
                                        "vl_pis_imp": parts[4], "dt_pag_pis": parts[5],
                                        "vl_bc_cofins": parts[6], "vl_cofins_imp": parts[7],
                                        "dt_pag_cofins": parts[8], "loc_exe_serv": parts[9]})
            elif registry == "A170" and ids["A100"]:
                ids["A170"] = len(block_a["A170"]) + 1
                block_a["A170"].append({"id_A170": ids["A170"], "id_A100": ids["A100"],
                                        "num_item": parts[2], "cod_item": parts[3],
                                        "descr_compl": parts[4], "vl_item": parts[5],
                                        "vl_desc": parts[6], "nat_bc_cred": parts[7],
                                        "ind_orig_cred": parts[8], "cst_pis": parts[9],
                                        "vl_bc_pis": parts[10], "aliq_pis": parts[11],
                                        "vl_pis": parts[12], "cst_cofins": parts[13],
                                        "vl_bc_cofins": parts[14], "aliq_cofins": parts[15],
                                        "vl_cofins": parts[16], "cod_cta": parts[17],
                                        "cod_ccus": parts[18]})
            elif registry == "A990" and ids["A001"]:
                ids["A990"] = len(block_a["A990"]) + 1
                block_a["A990"].append({"id_A990": ids["A990"], "id_A001": ids["A001"], "qtd_lin_a": parts[2]})

        return {reg: pd.DataFrame(table) for reg, table in block_a.items()}

    def parse_block_c(self, lines):
        """ Parse block C of a SPED file.
            Parameter:
            lines: list of strings.
            Returns a dictionary of DataFrame objects.
        """

        # Storage
        block_c = defaultdict(list)

        id_c001 = None
        id_c010 = None
        id_c100 = None
        id_c110 = None
        id_c111 = None
        id_c120 = None
        id_c170 = None
        id_c175 = None
        id_c180 = None
        id_c181 = None
        id_c185 = None
        id_c188 = None
        id_c190 = None
        id_c191 = None
        id_c195 = None
        id_c198 = None
        id_c199 = None
        id_c380 = None
        id_c381 = None
        id_c385 = None
        id_c395 = None
        id_c396 = None
        id_c400 = None
        id_c405 = None
        id_c481 = None
        id_c485 = None
        id_c491 = None
        id_c500 = None
        id_c501 = None
        id_c505 = None
        id_c509 = None
        id_c600 = None
        id_c601 = None
        id_c605 = None
        id_c609 = None
        id_c860 = None
        id_c870 = None
        id_c880 = None
        id_c890 = None
        id_c990 = None

        for line in lines:
            parts = line.strip().split("|")

            # Prevents index error when a file is malformed.
            if len(parts) < 2:
                continue

            registry = parts[1]

            if registry == "C001":
                id_c001 = len(block_c["C001"]) + 1
                block_c["C001"].append({"id_c001": id_c001, "ind_mov": parts[2]})
            elif registry == "C010" and id_c001:
                id_c010 = len(block_c["C010"]) + 1
                block_c["C010"].append({"id_c010": id_c010, "id_c001": id_c001,
                                        "cnpj": parts[2], "ind_escri": parts[3]})
            elif registry == "C100" and id_c010:
                id_c100 = len(block_c["C100"]) + 1
                block_c["C100"].append({"id_c100": id_c100, "id_c010": id_c010,
                                   "ind_oper": parts[2], "ind_emit": parts[3],
                                    "cod_part": parts[4], "cod_mod": parts[5],
                                    "cod_sit": parts[6], "ser": parts[7],
                                    "num_doc": parts[8], "chv_nfe": parts[9],
                                    "dt_doc": parts[10], "dt_e_s": parts[11],
                                    "vl_doc": parts[12], "ind_pgto": parts[13],
                                    "vl_desc": parts[14], "vl_abat_nt": parts[15],
                                    "vl_merc": parts[16], "ind_frt": parts[17],
                                    "vl_frt": parts[18], "vl_seg": parts[19],
                                    "vl_out_da": parts[20], "vl_bc_icms": parts[21],
                                    "vl_icms": parts[22], "vl_bc_icms_st": parts[23],
                                    "vl_icms_st": parts[24], "vl_ipi": parts[25],
                                    "vl_pis": parts[26], "vl_cofins": parts[27],
                                    "vl_pis_st": parts[28], "vl_cofins_st": parts[29]})
            elif registry == "C110" and id_c100:
                id_c110 = len(block_c["C110"]) + 1
                block_c["C110"].append({"id_c110": id_c110, "id_c100": id_c100,
                                    "cod_inf": parts[2], "txt_compl": parts[3]})
            elif registry == "C111" and id_c100:
                id_c111 = len(block_c["C111"]) + 1
                block_c["C111"].append({"id_c111": id_c111, "id_c100": id_c100,
                                    "num_proc": parts[2], "ind_proc": parts[3]})
            elif registry == "C120" and id_c100:
                id_c120 = len(block_c["C120"]) + 1
                block_c["C120"].append({"id_c120": id_c120, "id_c100": id_c100,
                                    "cod_doc_imp": parts[2], "num_doc_imp": parts[3],
                                    "vl_pis_imp": parts[4], "vl_cofins_imp": parts[5],
                                    "num_acd_raw": parts[6]})
            elif registry == "C170" and id_c100:
                id_c170 = len(block_c["C170"]) + 1
                block_c["C170"].append({"id_c170": id_c170, "id_c100": id_c100,
                                    "num_item": parts[2], "cod_item": parts[3],
                                    "descr_compl": parts[4], "qtd": parts[5],
                                    "unid": parts[6], "vl_item": parts[7],
                                    "vl_desc": parts[8],
                                    "ind_mov": parts[9], "cst_icms": parts[10],
                                    "cfop": parts[11], "cod_nat": parts[12],
                                    "vl_bc_icms": parts[13], "aliq_icms": parts[14],
                                    "vl_icms": parts[15], "vl_bc_icms_st": parts[16],
                                    "aliq_st": parts[17], "vl_icms_st": parts[18],
                                    "ind_apus": parts[19], "cst_ipi": parts[20],
                                    "cod_enq": parts[21], "vl_bc_ipi": parts[22],
                                    "aliq_ipi": parts[23], "vl_ipi": parts[24],
                                    "cst_pis": parts[25], "vl_bc_pis": parts[26],
                                    "aliq_pis": parts[27], "quant_bc_pis": parts[28],
                                    "aliq_pis_quant": parts[29], "vl_pis": parts[30],
                                    "cst_cofin": parts[31], "vl_bc_cofins": parts[32],
                                    "aliq_cofins": parts[33], "quant_bc_cofins": parts[34],
                                    "aliq_cofins_quant": parts[35], "vl_cofins": parts[36],
                                    "cod_cta": parts[37]})
            elif registry == "C175" and id_c100:
                id_c175 = len(block_c["C175"]) + 1
                block_c["C175"].append({"id_c175": id_c175, "id_c100": id_c100,
                                   "cfop": parts[2], "vl_opr": parts[3],
                                    "vl_desc": parts[4], "cst_pis": parts[5],
                                    "vl_bc_pis": parts[6], "aliq_pis": parts[7],
                                    "quant_bc_pis": parts[8], "aliq_pis_quant": parts[9],
                                    "vl_pis": parts[10], "cst_cofins": parts[11],
                                    "vl_bc_cofins": parts[12], "aliq_cofins": parts[13],
                                    "quant_bc_cofins": parts[14], "aliq_cofins_quant": parts[15],
                                    "vl_cofins": parts[16], "cod_cta": parts[17],
                                    "info_compl": parts[18]})
            elif registry == "C180" and id_c100:
                id_c180 = len(block_c["C180"]) + 1
                block_c["C180"].append({"id_c180": id_c180, "id_c100": id_c100,
                                    "cod_mod": parts[2], "dt_doc_ini": parts[3],
                                    "dt_doc_fin": parts[4], "cod_item": parts[5],
                                    "cod_ncm": parts[6], "ex_ipi": parts[7],
                                    "vl_tot_item": parts[8]})
            elif registry == "C181" and id_c180:
                id_c181 = len(block_c["C181"]) + 1
                block_c["C181"].append({"id_c181": id_c181, "id_c180": id_c180,
                                   "cst_pis": parts[2], "cfop": parts[3],
                                    "vl_item": parts[4], "vl_desc": parts[5],
                                    "vl_bc_pis": parts[6], "aliq_pis": parts[7],
                                    "quant_bc_pis": parts[8], "aliq_pis_quant": parts[9],
                                    "vl_pis": parts[10], "cod_cta": parts[11]})
            elif registry == "C185" and id_c180:
                id_c185 = len(block_c["C185"]) + 1
                block_c["C185"].append({"id_c185": id_c185, "id_c180": id_c180,
                                    "cst_cofins": parts[2], "cfop": parts[3],
                                    "vl_item": parts[4], "vl_desc": parts[5],
                                    "vl_bc_cofins": parts[6], "aliq_cofins": parts[7],
                                    "quant_bc_cofins": parts[8], "aliq_cofins_quant": parts[9],
                                    "vl_cofins": parts[10], "cod_cta": parts[11]})
            elif registry == "C188" and id_c180:
                id_c188 = len(block_c["C188"]) + 1
                block_c["C188"].append({"id_c188": id_c188, "id_c180": id_c180,
                                    "num_proc": parts[2], "ind_proc": parts[3]})
            elif registry == "C190" and id_c100:
                id_c190 = len(block_c["C190"]) + 1
                block_c["C190"].append({"id_c190": id_c190, "id_c100": id_c100,
                                    "cod_mod": parts[2], "dt_ref_ini": parts[3],
                                    "dt_ref_fin": parts[4], "cod_item": parts[5],
                                    "cod_ncm": parts[6], "ex_ipi": parts[7],
                                    "vl_tot_item": parts[8]})
            elif registry == "C191" and id_c190:
                id_c191 = len(block_c["C191"]) + 1
                block_c["C191"].append({"id_c191": id_c191, "id_c190": id_c190,
                                    "cnpj_cpf_part": parts[2], "cst_pis": parts[3],
                                    "cfop": parts[4], "vl_item": parts[5], "vl_desc": parts[6],
                                    "vl_bc_pis": parts[7], "aliq_pis": parts[8],
                                    "quant_bc_pis": parts[9], "aliq_pis_quant": parts[10],
                                    "vl_pis": parts[11], "cod_cta": parts[12]})
            elif registry == "C195" and id_c190:
                id_c195 = len(block_c["C195"]) + 1
                block_c["C195"].append({"id_c195": id_c195, "id_c190": id_c190,
                                    "cnpj_cpf_part": parts[2], "cst_cofins": parts[3],
                                    "cfop": parts[4], "vl_item": parts[5], "vl_desc": parts[6],
                                    "vl_bc_cofins": parts[7], "aliq_cofins": parts[8],
                                    "quant_bc_cofins": parts[9], "aliq_cofins_quant": parts[10],
                                    "vl_cofins": parts[11], "cod_cta": parts[12]})
            elif registry == "C198" and id_c190:
                id_c198 = len(block_c["C198"]) + 1
                block_c["C198"].append({"id_c198": id_c198, "id_c190": id_c190,
                                    "num_proc": parts[2], "ind_proc": parts[3]})
            elif registry == "C199" and id_c190:
                id_c199 = len(block_c["C199"]) + 1
                block_c["C199"].append({"id_c199": id_c199, "id_c190": id_c190,
                                    "cod_doc_imp": parts[2], "num_doc_imp": parts[3],
                                    "vl_pis_imp": parts[4], "vl_cofins_imp": parts[5],
                                    "num_acdraw": parts[6]})
            elif registry == "C380" and id_c100:
                id_c380 = len(block_c["C380"]) + 1
                block_c["C380"].append({"id_c380": id_c380, "id_c100": id_c100,
                                    "cod_mod": parts[2], "dt_doc_ini": parts[3],
                                    "dt_doc_fin": parts[4], "num_doc_ini": parts[5],
                                    "num_doc_fin": parts[6], "vl_doc": parts[7],
                                    "vl_doc_canc": parts[8]})
            elif registry == "C381" and id_c380:
                id_c381 = len(block_c["C381"]) + 1
                block_c["C381"].append({"id_c381": id_c381, "id_c380": id_c380,
                                    "cst_pis": parts[2], "cod_item": parts[3],
                                    "vl_item": parts[4], "vl_bc_pis": parts[5],
                                    "aliq_pis": parts[6], "quant_bc_pis": parts[7],
                                    "aliq_pis_quant": parts[8], "vl_pis": parts[9],
                                    "cod_cta": parts[10]})
            elif registry == "C385" and id_c380:
                id_c385 = len(block_c["C385"]) + 1
                block_c["C385"].append({"id_c385": id_c385, "id_c380": id_c380,
                                    "cst_cofins": parts[2], "cod_item": parts[3],
                                    "vl_item": parts[4], "vl_bc_cofins": parts[5],
                                    "aliq_cofins": parts[6], "quant_bc_cofins": parts[7],
                                    "aliq_cofins_quant": parts[8], "vl_cofins": parts[9],
                                    "cod_cta": parts[10]})
            elif registry == "C395" and id_c100:
                id_c395 = len(block_c["C395"]) + 1
                block_c["C395"].append({"id_c395": id_c395, "id_c100": id_c100,
                                    "cod_mod": parts[2], "cod_part": parts[3],
                                    "ser": parts[4], "sub_ser": parts[5],
                                    "num_doc": parts[6], "dt_doc": parts[7],
                                    "vl_doc": parts[8]})
            elif registry == "C396" and id_c100:
                id_c396 = len(block_c["C396"]) + 1
                block_c["C396"].append({"id_c396": id_c396, "id_c100": id_c100,
                                    "cod_item": parts[2], "vl_item": parts[3],
                                    "vl_desc": parts[4], "nat_bc_cred": parts[5],
                                    "cst_pis": parts[6], "vl_bc_pis": parts[7],
                                    "aliq_pis": parts[8], "vl_pis": parts[9],
                                    "cst_cofins": parts[10], "vl_bc_cofins": parts[11],
                                    "aliq_cofins": parts[12], "vl_cofins": parts[13],
                                    "cod_cta": parts[14]})
            elif registry == "C400" and id_c100:
                id_c400 = len(block_c["C400"]) + 1
                block_c["C400"].append({"id_c400": id_c400, "id_c100": id_c100,
                                    "cod_mod": parts[2], "ecf_mod": parts[3],
                                    "ecf_fab": parts[4], "ecf_cx": parts[5]})
            elif registry == "C405" and id_c400:
                id_c405 = len(block_c["C405"]) + 1
                block_c["C405"].append({"id_c405": id_c405, "id_c400": id_c400,
                                    "dt_doc": parts[2], "cro": parts[3],
                                    "crz": parts[4], "num_coo_fin": parts[5],
                                    "gt_fin": parts[6], "vl_brt": parts[7]})
            elif registry == "C481" and id_c405:
                id_c481 = len(block_c["C481"]) + 1
                block_c["C481"].append({"id_c481": id_c481, "id_c405": id_c405,
                                   "cst_pis": parts[2], "vl_item": parts[3],
                                    "vl_bc_pis": parts[4], "aliq_pis": parts[5],
                                    "quant_bc_pis": parts[6], "aliq_pis_quant": parts[7],
                                    "vl_pis": parts[8], "cod_item": parts[9],
                                    "cod_cta": parts[10]})
            elif registry == "C485" and id_c405:
                id_c485 = len(block_c["C485"]) + 1
                block_c["C485"].append({"id_c485": id_c485, "id_c405": id_c405,
                                    "cst_cofins": parts[2], "vl_item": parts[3],
                                    "vl_bc_cofins": parts[4], "aliq_cofins": parts[5],
                                    "quant_bc_cofins": parts[6], "aliq_cofins_quant": parts[7],
                                    "vl_cofins": parts[8], "cod_item": parts[9],
                                    "cod_cta": parts[10]})
            elif registry == "C489" and id_c405:
                id_c489 = len(block_c["C489"]) + 1
                block_c["C489"].append({"id_c489": id_c489, "id_c405": id_c405,
                                    "num_proc": parts[2], "ind_proc": parts[3]})
            elif registry == "C490" and id_c400:
                id_c490 = len(block_c["C490"]) + 1
                block_c["C490"].append({"id_c490": id_c490, "id_c400": id_c400,
                                    "dt_doc_ini": parts[2], "dt_doc_fin": parts[3],
                                    "cod_mod": parts[4]})
            elif registry == "C491" and id_c490:
                id_c491 = len(block_c["C491"]) + 1
                block_c["C491"].append({"id_c491": id_c491, "id_c490": id_c490,
                                    "cod_item": parts[2], "cst_pis": parts[3],
                                    "cfop": parts[4], "vl_item": parts[5],
                                    "vl_bc_pis": parts[6], "aliq_pis": parts[7],
                                    "quant_bc_pis": parts[8], "aliq_pis_quant": parts[9],
                                    "vl_pis": parts[10], "cod_cta": parts[11]})
            elif registry == "C495" and id_c490:
                id_c495 = len(block_c["C495"]) + 1
                block_c["C495"].append({"id_c495": id_c495, "id_c490": id_c490,
                                    "cod_item": parts[2], "cst_cofins": parts[3],
                                    "cfop": parts[4], "vl_item": parts[5],
                                    "vl_bc_cofins": parts[6], "aliq_cofins": parts[7],
                                    "quant_bc_cofins": parts[8], "aliq_cofins_quant": parts[9],
                                    "vl_cofins": parts[10], "cod_cta": parts[11]})
            elif registry == "C499" and id_c490:
                id_c499 = len(block_c["C499"]) + 1
                block_c["C499"].append({"id_c499": id_c499, "id_c490": id_c490,
                                    "num_proc": parts[2], "ind_proc": parts[3]})
            elif registry == "C500" and id_c100:
                id_c500 = len(block_c["C500"]) + 1
                block_c["C500"].append({"id_c500": id_c500, "id_c100": id_c100,
                                    "cod_part": parts[2], "cod_mod": parts[3],
                                    "cod_sit": parts[4], "ser": parts[5],
                                    "sub": parts[6], "num_doc": parts[7],
                                    "dt_doc": parts[8], "dt_ent": parts[9],
                                    "vl_doc": parts[10], "vl_icms": parts[11],
                                    "cod_inf": parts[12], "vl_pis": parts[13],
                                    "vl_cofins": parts[14], "chv_doce": parts[15]})
            elif registry == "C501" and id_c500:
                id_c501 = len(block_c["C501"]) + 1
                block_c["C501"].append({"id_c501": id_c501, "id_c500": id_c500,
                                    "cst_pis": parts[2], "vl_item": parts[3],
                                    "nat_bc_cred": parts[4], "vl_bc_pis": parts[5],
                                    "aliq_pis": parts[6], "vl_pis": parts[7],
                                    "cod_cta": parts[8]})
            elif registry == "C505" and id_c500:
                id_c505 = len(block_c["C505"]) + 1
                block_c["C505"].append({"id_c505": id_c505, "id_c500": id_c500,
                                    "cst_cofins": parts[2], "vl_item": parts[3],
                                    "nat_bc_cred": parts[4], "vl_bc_cofins": parts[5],
                                    "aliq_cofins": parts[6], "vl_cofins": parts[7],
                                    "cod_cta": parts[8]})
            elif registry == "C509" and id_c500:
                id_c509 = len(block_c["C509"]) + 1
                block_c["C509"].append({"id_c509": id_c509, "id_c500": id_c500,
                                    "num_proc": parts[2], "ind_proc": parts[3]})
            elif registry == "C600" and id_c100:
                id_c600 = len(block_c["C600"]) + 1
                block_c["C600"].append({"id_c600": id_c600, "id_c100": id_c100, "cod_mod": parts[2],
                                    "cod_mun": parts[3], "ser": parts[4], "sub": parts[5],
                                    "cod_cons": parts[6], "qtd_cons": parts[7],
                                    "qtd_canc": parts[8], "dt_doc": parts[9],
                                    "vl_doc": parts[10], "vl_desc": parts[11],
                                    "cons": parts[12], "vl_forn": parts[13],
                                    "vl_serv_nt": parts[14], "vl_terc": parts[15],
                                    "vl_da": parts[16], "vl_bc_icms": parts[17],
                                    "vl_icms": parts[18], "vl_bc_icms_st": parts[19],
                                    "vl_icms_st": parts[20], "vl_pis": parts[21],
                                    "vl_cofins": parts[22]})
            elif registry == "C601" and id_c600:
                id_c601 = len(block_c["C601"]) + 1
                block_c["C601"].append({"id_c601": id_c601, "id_c600": id_c600,
                                    "cst_pis": parts[2], "vl_item": parts[3],
                                    "vl_bc_pis": parts[4], "aliq_pis": parts[5],
                                    "vl_pis": parts[6], "cod_cta": parts[7]})
            elif registry == "C605" and id_c600:
                id_c605 = len(block_c["C605"]) + 1
                block_c["C605"].append({"id_c605": id_c605, "id_c600": id_c600,
                                    "cst_cofins": parts[2], "vl_item": parts[3],
                                    "vl_bc_cofins": parts[4], "aliq_cofins": parts[5],
                                    "vl_cofins": parts[6], "cod_cta": parts[7]})
            elif registry == "C609" and id_c600:
                id_c609 = len(block_c["C609"]) + 1
                block_c["C609"].append({"id_c609": id_c609, "id_c600": id_c600,
                                    "num_proc": parts[2], "ind_proc": parts[3]})
            elif registry == "C860" and id_c100:
                id_c860 = len(block_c["C860"]) + 1
                block_c["C860"].append({"id_c860": id_c860, "id_c100": id_c100,
                                    "cod_mod": parts[2],
                                    "nr_sat": parts[3], "dt_doc": parts[4],
                                    "doc_ini": parts[5], "doc_fim": parts[6]})
            elif registry == "C870" and id_c860:
                id_c870 = len(block_c["C870"]) + 1
                block_c["C870"].append({"id_c870": id_c870, "id_c860": id_c860,
                                    "cod_item": parts[2],
                                    "cfop": parts[3], "vl_item": parts[4],
                                    "vl_desc": parts[5], "cst_pis": parts[6],
                                    "vl_bc_pis": parts[7], "aliq_pis": parts[8],
                                    "vl_pis": parts[9], "cst_cofins": parts[10],
                                    "vl_bc_cofins": parts[11], "aliq_cofins": parts[12],
                                    "vl_cofins": parts[13], "cod_cta": parts[14]})
            elif registry == "C880" and id_c860:
                id_c880 = len(block_c["C880"]) + 1
                block_c["C880"].append({"id_c880": id_c880, "id_c860": id_c860,
                                    "cod_item": parts[2],
                                    "cfop": parts[3], "vl_item": parts[4],
                                    "vl_desc": parts[5], "cst_pis": parts[6],
                                    "quant_bc_pis": parts[7], "aliq_pis_quant": parts[8],
                                    "vl_pis": parts[9], "cst_cofins": parts[10],
                                    "quant_bc_cofins": parts[11], "aliq_cofins_quant": parts[12],
                                    "vl_cofins": parts[13], "cod_cta": parts[14]})
            elif registry == "C890" and id_c860:
                id_c890 = len(block_c["C890"]) + 1
                block_c["C890"].append({"id_c890": id_c890, "id_c860": id_c860,
                                        "num_proc": parts[2], "ind_proc": parts[3]})
            elif registry == "C990" and id_c001:
                id_c990 = len(block_c["C990"]) + 1
                block_c["C990"].append({"id_c990": id_c990, "id_c001": id_c001, "qtd_lin_c": parts[2]})

        return {reg: pd.DataFrame(table) for reg, table in block_c.items()}

    def parse_block_d(self, lines):
        """ Parse block D of a SPED file.
            Parameter:
            lines: list of strings.
            Returns a dictionary of DataFrame objects.
        """
        block_d = defaultdict(list)

        ids = {'D001': None,
               'D010': None,
               'D100': None,
               'D101': None,
               'D105': None,
               'D111': None,
               'D200': None,
               'D201': None,
               'D205': None,
               'D209': None,
               'D300': None,
               'D309': None,
               'D350': None,
               'D359': None,
               'D500': None,
               'D501': None,
               'D505': None,
               'D509': None,
               'D600': None,
               'D601': None,
               'D605': None,
               'D609': None,
               'D990': None}

        for line in lines:
            parts = line.strip().split("|")

            # Prevents index error when a file is malformed.
            if len(parts) < 2:
                continue

            registry = parts[1]

            if registry == "D001":
                ids["D001"] = len(block_d["D001"]) + 1
                block_d["D001"].append({"id_D001": ids["D001"], "ind_mov": parts[2]})
            elif registry == "D010" and ids["D001"]:
                ids["D010"] = len(block_d["D010"]) + 1
                block_d["D010"].append({"id_D010": ids["D010"], "id_D001": ids["D001"],
                                        "cnpj": parts[2]})
            elif registry == "D100" and ids["D001"]:
                ids["D100"] = len(block_d["D100"]) + 1
                block_d["D100"].append({"id_D100": ids["D100"], "id_D001": ids["D001"],
                                        "ind_oper": parts[2], "ind_emit": parts[3],
                                        "cod_part": parts[4], "cod_mod": parts[5],
                                        "cod_sit": parts[6], "ser": parts[7],
                                        "sub": parts[8], "num_doc": parts[9],
                                        "chv_cte": parts[10], "dt_doc": parts[11],
                                        "dt_a_p": parts[12], "tp_cte": parts[13],
                                        "chv_cte_ref": parts[14], "vl_doc": parts[15],
                                        "vl_desc": parts[16], "ind_frt": parts[17],
                                        "vl_serv": parts[18], "vl_bc_icms": parts[19],
                                        "vl_icms": parts[20], "vl_nt": parts[21],
                                        "cod_inf": parts[22], "cod_cta": parts[23]})
            elif registry == "D101" and ids["D100"]:
                ids["D101"] = len(block_d["D101"]) + 1
                block_d["D101"].append({"id_D101": ids["D101"], "id_D100": ids["D100"],
                                        "ind_nat_frt": parts[2], "vl_item": parts[3],
                                        "cst_pis": parts[4], "nat_bc_cred": parts[5],
                                        "vl_bc_pis": parts[6], "aliq_pis": parts[7],
                                        "vl_pis": parts[8], "cod_cta": parts[9]})
            elif registry == "D105" and ids["D100"]:
                ids["D105"] = len(block_d["D105"]) + 1
                block_d["D105"].append({"id_D105": ids["D105"], "id_D100": ids["D100"],
                                        "ind_nat_frt": parts[2], "vl_item": parts[3],
                                        "cst_cofins": parts[4], "nat_bc_cred": parts[5],
                                        "vl_bc_cofins": parts[6], "aliq_cofins": parts[7],
                                        "vl_cofins": parts[8], "cod_cta": parts[9]})
            elif registry == "D111" and ids["D100"]:
                ids["D111"] = len(block_d["D111"]) + 1
                block_d["D111"].append({"id_D111": ids["D111"], "id_D100": ids["D100"],
                                        "num_proc": parts[2], "ind_proc": parts[3]})
            elif registry == "D200" and ids["D001"]:
                ids["D200"] = len(block_d["D200"]) + 1
                block_d["D200"].append({"id_D200": ids["D200"], "id_D001": ids["D001"],
                                        "cod_mod": parts[2], "cod_sit": parts[3],
                                        "ser": parts[4], "sub": parts[5],
                                        "num_doc_ini": parts[6], "num_doc_fin": parts[7],
                                        "cfop": parts[8], "dt_ref": parts[9],
                                        "vl_doc": parts[10], "vl_desc": parts[11]})
            elif registry == "D201" and ids["D200"]:
                ids["D201"] = len(block_d["D201"]) + 1
                block_d["D201"].append({"id_D201": ids["D201"], "id_D200": ids["D200"],
                                        "cst_pis": parts[2], "vl_item": parts[3],
                                        "vl_bc_pis": parts[4], "aliq_pis": parts[5],
                                        "vl_pis": parts[6], "cod_cta": parts[7]})
            elif registry == "D205" and ids["D200"]:
                ids["D205"] = len(block_d["D205"]) + 1
                block_d["D205"].append({"id_D205": ids["D205"], "id_D200": ids["D200"],
                                        "cst_cofins": parts[2], "vl_item": parts[3],
                                        "vl_bc_cofins": parts[4], "aliq_cofins": parts[5],
                                        "vl_cofins": parts[6], "cod_cta": parts[7]})
            elif registry == "D209" and ids["D200"]:
                ids["D209"] = len(block_d["D209"]) + 1
                block_d["D209"].append({"id_D209": ids["D209"], "id_D200": ids["D200"],
                                        "num_proc": parts[2], "ind_proc": parts[3]})
            elif registry == "D300" and ids["D001"]:
                ids["D300"] = len(block_d["D300"]) + 1
                block_d["D300"].append({"id_D300": ids["D300"], "id_D001": ids["D001"],
                                        "cod_mod": parts[2], "ser": parts[3],
                                        "sub": parts[4], "num_doc_ini": parts[5],
                                        "num_doc_fin": parts[6], "cfop": parts[7],
                                        "dt_ref": parts[8], "vl_doc": parts[9],
                                        "vl_desc": parts[10], "cst_pis": parts[11],
                                        "vl_bc_pis": parts[12], "aliq_pis": parts[13],
                                        "vl_pis": parts[14], "cst_cofins": parts[15],
                                        "vl_bc_cofins": parts[16], "aliq_cofins": parts[17],
                                        "vl_cofins": parts[18], "cod_cta": parts[19]})
            elif registry == "D309" and ids["D300"]:
                ids["D309"] = len(block_d["D309"]) + 1
                block_d["D309"].append({"id_D309": ids["D309"], "id_D300": ids["D300"],
                                        "num_proc": parts[2], "ind_proc": parts[3]})
            elif registry == "D350" and ids["D001"]:
                ids["D350"] = len(block_d["D350"]) + 1
                block_d["D350"].append({"id_D350": ids["D350"], "id_D001": ids["D001"],
                                        "cod_mod": parts[2], "ecf_mod": parts[3],
                                        "ecf_fab": parts[4], "dt_doc": parts[5],
                                        "cro": parts[6], "crz": parts[7],
                                        "num_coo_fin": parts[8], "gt_fin": parts[9],
                                        "vl_brt": parts[10], "cst_pis": parts[11],
                                        "vl_bc_pis": parts[12], "aliq_pis": parts[13],
                                        "quant_bc_pis": parts[14], "aliq_pis_quant": parts[15],
                                        "vl_pis": parts[16], "cst_cofins": parts[17],
                                        "vl_bc_cofins": parts[18], "aliq_cofins": parts[19],
                                        "quant_bc_cofins": parts[20], "aliq_cofins_quant": parts[21],
                                        "vl_cofins": parts[22], "cod_cta": parts[23]})
            elif registry == "D359" and ids["D350"]:
                ids["D359"] = len(block_d["D359"]) + 1
                block_d["D359"].append({"id_D359": ids["D359"], "id_D350": ids["D350"],
                                        "num_proc": parts[2], "ind_proc": parts[3]})
            elif registry == "D500" and ids["D001"]:
                ids["D500"] = len(block_d["D500"]) + 1
                block_d["D500"].append({"id_D500": ids["D500"], "id_D001": ids["D001"],
                                        "ind_oper": parts[2], "ind_emit": parts[3],
                                        "cod_part": parts[4], "cod_mod": parts[5],
                                        "cod_sit": parts[6], "ser": parts[7],
                                        "sub": parts[8], "num_doc": parts[9],
                                        "dt_doc": parts[10], "dt_a_p": parts[11],
                                        "vl_doc": parts[12], "vl_desc": parts[13],
                                        "vl_serv": parts[14], "vl_serv_nt": parts[15],
                                        "vl_terc": parts[16], "vl_da": parts[17],
                                        "vl_bc_icms": parts[18], "vl_icms": parts[19],
                                        "cod_inf": parts[20], "vl_pis": parts[21],
                                        "vl_cofins": parts[22]})
            elif registry == "D501" and ids["D500"]:
                ids["D501"] = len(block_d["D501"]) + 1
                block_d["D501"].append({"id_D501": ids["D501"], "id_D500": ids["D500"],
                                        "cst_pis": parts[2], "vl_item": parts[3],
                                        "nat_bc_cred": parts[4], "vl_bc_pis": parts[5],
                                        "aliq_pis": parts[6], "vl_pis": parts[7],
                                        "cod_cta": parts[8]})
            elif registry == "D505" and ids["D500"]:
                ids["D505"] = len(block_d["D505"]) + 1
                block_d["D505"].append({"id_D505": ids["D505"], "id_D500": ids["D500"],
                                        "cst_cofins": parts[2], "vl_item": parts[3],
                                        "nat_bc_cred": parts[4], "vl_bc_cofins": parts[5],
                                        "aliq_cofins": parts[6], "vl_cofins": parts[7],
                                        "cod_cta": parts[8]})
            elif registry == "D509" and ids["D500"]:
                ids["D509"] = len(block_d["D509"]) + 1
                block_d["D509"].append({"id_D509": ids["D509"], "id_D500": ids["D500"],
                                        "num_proc": parts[2], "ind_proc": parts[3]})
            elif registry == "D600" and ids["D001"]:
                ids["D600"] = len(block_d["D600"]) + 1
                block_d["D600"].append({"id_D600": ids["D600"], "id_D001": ids["D001"],
                                        "cod_mod": parts[2], "cod_mun": parts[3],
                                        "ser": parts[4], "sub": parts[5],
                                        "ind_rec": parts[6], "qtd_cons": parts[7],
                                        "dt_doc_ini": parts[8], "dt_doc_fin": parts[9],
                                        "vl_doc": parts[10], "vl_desc": parts[11],
                                        "vl_serv": parts[12], "vl_serv_nt": parts[13],
                                        "vl_terc": parts[14], "vl_da": parts[15],
                                        "vl_bc_icms": parts[16], "vl_icms": parts[17],
                                        "vl_pis": parts[18], "vl_cofins": parts[19]})
            elif registry == "D601" and ids["D600"]:
                ids["D601"] = len(block_d["D601"]) + 1
                block_d["D601"].append({"id_D601": ids["D601"], "id_D600": ids["D600"],
                                        "cod_class": parts[2], "vl_item": parts[3],
                                        "vl_desc": parts[4], "cst_pis": parts[5],
                                        "vl_bc_pis": parts[6], "aliq_pis": parts[7],
                                        "vl_pis": parts[8], "cod_cta": parts[9]})
            elif registry == "D605" and ids["D600"]:
                ids["D605"] = len(block_d["D605"]) + 1
                block_d["D605"].append({"id_D605": ids["D605"], "id_D600": ids["D600"],
                                        "cod_class": parts[2], "vl_item": parts[3],
                                        "vl_desc": parts[4], "cst_cofins": parts[5],
                                        "vl_bc_cofins": parts[6], "aliq_cofins": parts[7],
                                        "vl_cofins": parts[8], "cod_cta": parts[9]})
            elif registry == "D609" and ids["D600"]:
                ids["D609"] = len(block_d["D609"]) + 1
                block_d["D609"].append({"id_D609": ids["D609"], "id_D600": ids["D600"],
                                        "num_proc": parts[2], "ind_proc": parts[3]})
            elif registry == "D990" and ids["D001"]:
                ids["D990"] = len(block_d["D990"]) + 1
                block_d["D990"].append({"id_D990": ids["D990"], "id_D001": ids["D001"], "qtd_lin_d": parts[2]})

        return {reg: pd.DataFrame(table) for reg, table in block_d.items()}

    def parse_block_f(self, lines):
        """ Parse block F of a SPED file.
            Parameter:
            lines: list of strings.
            Returns a dictionary of DataFrame objects.
        """
        block_f = defaultdict(list)

        ids = {'F001': None,
               'F010': None,
               'F100': None,
               'F111': None,
               'F120': None,
               'F130': None,
               'F139': None,
               'F150': None,
               'F200': None,
               'F205': None,
               'F210': None,
               'F211': None,
               'F500': None,
               'F509': None,
               'F510': None,
               'F519': None,
               'F525': None,
               'F550': None,
               'F559': None,
               'F560': None,
               'F569': None,
               'F600': None,
               'F700': None,
               'F800': None,
               'F990': None}

        for line in lines:
            parts = line.strip().split("|")

            # Prevents index error when a file is malformed.
            if len(parts) < 2:
                continue

            registry = parts[1]

            if registry == "F001":
                ids["F001"] = len(block_f["F001"]) + 1
                block_f["F001"].append({"id_F001": ids["F001"], "ind_mov": parts[2]})
            elif registry == "F010" and ids["F001"]:
                ids["F010"] = len(block_f["F010"]) + 1
                block_f["F010"].append({"id_F010": ids["F010"], "id_F001": ids["F001"],
                                        "cnpj": parts[2]})
            elif registry == "F100" and ids["F010"]:
                ids["F100"] = len(block_f["F100"]) + 1
                block_f["F100"].append({"id_F100": ids["F100"], "id_F010": ids["F010"],
                                        "ind_oper": parts[2], "cod_part": parts[3],
                                        "cod_item": parts[4], "dt_oper": parts[5],
                                        "vl_oper": parts[6], "cst_pis": parts[7],
                                        "vl_bc_pis": parts[8], "aliq_pis": parts[9],
                                        "vl_pis": parts[10], "cst_cofins": parts[11],
                                        "vl_bc_cofins": parts[12], "aliq_cofins": parts[13],
                                        "vl_cofins": parts[14], "nat_bc_cred": parts[15],
                                        "ind_orig_cred": parts[16], "cod_cta": parts[17],
                                        "cod_ccus": parts[18], "desc_doc_oper": parts[19]})
            elif registry == "F111" and ids["F100"]:
                ids["F111"] = len(block_f["F111"]) + 1
                block_f["F111"].append({"id_F111": ids["F111"], "id_F100": ids["F100"],
                                        "num_proc": parts[2], "ind_proc": parts[3]})
            elif registry == "F120" and ids["F010"]:
                ids["F120"] = len(block_f["F120"]) + 1
                block_f["F120"].append({"id_F120": ids["F120"], "id_F010": ids["F010"],
                                        "nat_bc_cred": parts[2], "ident_bem_imob": parts[3],
                                        "ind_orig_cred": parts[4], "ind_util_bem_imob": parts[5],
                                        "vl_oper_dep": parts[6], "parc_oper_nao_bc_cred": parts[7],
                                        "cst_pis": parts[8], "vl_bc_pis": parts[9],
                                        "aliq_pis": parts[10], "vl_pis": parts[11],
                                        "cst_cofins": parts[12], "vl_bc_cofins": parts[13],
                                        "aliq_cofins": parts[14], "vl_cofins": parts[15],
                                        "cod_cta": parts[16], "cod_ccus": parts[17],
                                        "desc_bem_imob": parts[18]})
            elif registry == "F129" and ids["F120"]:
                ids["F129"] = len(block_f["F129"]) + 1
                block_f["F129"].append({"id_F129": ids["F129"], "id_F120": ids["F120"],
                                        "num_proc": parts[2], "ind_proc": parts[3]})
            elif registry == "F130" and ids["F010"]:
                ids["F130"] = len(block_f["F130"]) + 1
                block_f["F130"].append({"id_F130": ids["F130"], "id_F010": ids["F010"],
                                        "nat_bc_cred": parts[2], "ident_bem_imob": parts[3],
                                        "idn_orig_cred": parts[4], "ind_util_bem_imob": parts[5],
                                        "mes_oper_aquis": parts[6], "vl_oper_aquis": parts[7],
                                        "parc_oper_nao_bc_cred": parts[8], "vl_bc_cred": parts[9],
                                        "ind_nr_parc": parts[10], "cst_pis": parts[11],
                                        "vl_bc_pis": parts[12], "aliq_pis": parts[13],
                                        "vl_pis": parts[14], "cst_cofins": parts[15],
                                        "vl_bc_cofins": parts[16], "aliq_cofins": parts[17],
                                        "vl_cofins": parts[18], "cod_cta": parts[19],
                                        "cod_ccus": parts[20], "desc_bem_imob": parts[21]})
            elif registry == "F139" and ids["F130"]:
                ids["F139"] = len(block_f["F139"]) + 1
                block_f["F139"].append({"id_F139": ids["F130"], "id_F130": ids["F130"],
                                        "num_proc": parts[2], "ind_proc": parts[3]})
            elif registry == "F150" and ids["F010"]:
                ids["F150"] = len(block_f["F150"]) + 1
                block_f["F150"].append({"id_F150": ids["F150"], "id_F010": ids["F010"],
                                        "nat_bc_cred": parts[2], "vl_tot_est": parts[3],
                                        "est_imp": parts[4], "vl_bc_est": parts[5],
                                        "vl_bc_men_est": parts[6], "cst_pis": parts[7],
                                        "aliq_pis": parts[8], "vl_cred_pis": parts[9],
                                        "cst_cofins": parts[10], "aliq_cofins": parts[11],
                                        "vl_cred_cofins": parts[12], "desc_est": parts[13],
                                        "cod_cta": parts[14]})
            elif registry == "F200" and ids["F010"]:
                ids["F200"] = len(block_f["F200"]) + 1
                block_f["F200"].append({"id_F200": ids["F200"], "id_F010": ids["F010"],
                                        "ind_oper": parts[2], "unid_imob": parts[3],
                                        "indent_emp": parts[4], "desc_unid_imob": parts[5],
                                        "num_cont": parts[6], "cpf_cnpj_adqu": parts[7],
                                        "dt_oper": parts[8], "vl_tot_vend": parts[9],
                                        "vl_rec_acum": parts[10], "vl_tot_rec": parts[11],
                                        "cst_pis": parts[12], "vl_bc_pis": parts[13],
                                        "aliq_pis": parts[14], "vl_pis": parts[15],
                                        "cst_cofins": parts[16], "vl_bc_cofins": parts[17],
                                        "aliq_cofins": parts[18], "vl_cofins": parts[19],
                                        "perc_rec_receb": parts[20], "ind_nat_emp": parts[21],
                                        "inf_comp": parts[22]})
            elif registry == "F205" and ids["F200"]:
                ids["F205"] = len(block_f["F205"]) + 1
                block_f["F205"].append({"id_F205": ids["F205"], "id_F200": ids["F200"],
                                        "vl_cus_inc_acum_ant": parts[2], "vl_cus_inc_per_esc": parts[3],
                                        "vl_cus_inc_acum": parts[4], "vl_exc_bc_cus_inc_acum": parts[5],
                                        "vl_bc_cus_inc": parts[6], "cst_pis": parts[7], "aliq_pis": parts[8],
                                        "vl_cred_pis_acum": parts[9], "vl_cred_pis_desc_ant": parts[10],
                                        "vl_cred_pis_desc": parts[11], "vl_cred_pis_desc_fut": parts[12],
                                        "cst_cofins": parts[13], "aliq_cofins": parts[14],
                                        "vl_cred_cofins_acum": parts[15], "vl_cred_cofins_desc_ant": parts[16],
                                        "vl_cred_cofins_desc": parts[17], "vl_cred_cofins_desc_fut": parts[18]})
            elif registry == "F210" and ids["F200"]:
                ids["F210"] = len(block_f["F210"]) + 1
                block_f["F210"].append({"id_F210": ids["F210"], "id_F200": ids["F200"],
                                        "vl_cus_orc": parts[2], "vl_exc": parts[3],
                                        "vl_cus_orc_aju": parts[4], "vl_bc_cred": parts[5],
                                        "cst_pis": parts[6], "aliq_pis": parts[7],
                                        "vl_cred_pis_util": parts[8], "cst_cofins": parts[9],
                                        "aliq_cofins": parts[10], "vl_cred_cofins_util": parts[11]})
            elif registry == "F211" and ids["F200"]:
                ids["F211"] = len(block_f["F211"]) + 1
                block_f["F211"].append({"id_F211": ids["F211"], "id_F200": ids["F200"],
                                        "num_proc": parts[2], "ind_proc": parts[3]})
            elif registry == "F500" and ids["F010"]:
                ids["F500"] = len(block_f["F500"]) + 1
                block_f["F500"].append({"id_F500": ids["F500"], "id_F010": ids["F010"],
                                        "vl_rec_caixa": parts[2], "cst_pis": parts[3],
                                        "vl_desc_pis": parts[4], "vl_bc_pis": parts[5],
                                        "aliq_pis": parts[6], "vl_pis": parts[7],
                                        "cst_cofins": parts[8], "vl_desc_cofins": parts[9],
                                        "vl_bc_cofins": parts[10], "aliq_cofins": parts[11],
                                        "vl_cofins": parts[12], "cod_mod": parts[13],
                                        "cfop": parts[14], "cod_cta": parts[15],
                                        "info_compl": parts[16]})
            elif registry == "F509" and ids["F500"]:
                ids["F509"] = len(block_f["F509"]) + 1
                block_f["F509"].append({"id_F509": ids["F509"], "id_F500": ids["F500"],
                                        "num_proc": parts[2], "ind_proc": parts[3]})
            elif registry == "F510" and ids["F500"]:
                ids["F510"] = len(block_f["F510"]) + 1
                block_f["F510"].append({"id_F510": ids["F510"], "id_F500": ids["F500"],
                                        "vl_rec_caixa": parts[2], "cst_pis": parts[3],
                                        "vl_desc_pis": parts[4], "quant_bc_pis": parts[5],
                                        "aliq_pis_quant": parts[6], "vl_pis": parts[7],
                                        "cst_cofins": parts[8], "vl_desc_cofins": parts[9],
                                        "quant_bc_cofins": parts[10], "aliq_cofins_quant": parts[11],
                                        "vl_cofins": parts[12], "cod_mod": parts[13],
                                        "cfop": parts[14], "cod_cta": parts[15],
                                        "info_compl": parts[16]})
            elif registry == "F519" and ids["F500"]:
                ids["F519"] = len(block_f["F519"]) + 1
                block_f["F519"].append({"id_F519": ids["F519"], "id_F500": ids["F500"],
                                        "num_proc": parts[2], "ind_proc": parts[3]})
            elif registry == "F525" and ids["F010"]:
                ids["F525"] = len(block_f["F525"]) + 1
                block_f["F525"].append({"id_F525": ids["F525"], "id_F010": ids["F010"],
                                        "vl_rec": parts[2], "ind_rec": parts[3],
                                        "cnpj_cpf": parts[4], "num_doc": parts[5],
                                        "cod_item": parts[6], "vl_rec_det": parts[7],
                                        "cst_pis": parts[8], "cst_cofins": parts[9],
                                        "info_compl": parts[10], "cod_cta": parts[11]})
            elif registry == "F550" and ids["F010"]:
                ids["F550"] = len(block_f["F550"]) + 1
                block_f["F550"].append({"id_F550": ids["F550"], "id_F010": ids["F010"],
                                        "vl_rec_comp": parts[2], "cst_pis": parts[3],
                                        "vl_desc_pis": parts[4], "vl_bc_pis": parts[5],
                                        "aliq_pis": parts[6], "vl_pis": parts[7],
                                        "cst_cofins": parts[8], "vl_desc_cofins": parts[9],
                                        "vl_bc_cofins": parts[10], "aliq_cofins": parts[11],
                                        "vl_cofins": parts[12], "cod_mod": parts[13],
                                        "cfop": parts[14], "cod_cta": parts[15],
                                        "info_compl": parts[16]})
            elif registry == "F559" and ids["F550"]:
                ids["F559"] = len(block_f["F559"]) + 1
                block_f["F559"].append({"id_F559": ids["F559"], "id_F550": ids["F550"],
                                        "num_proc": parts[2], "ind_proc": parts[3]})
            elif registry == "F560" and ids["F010"]:
                ids["F560"] = len(block_f["F560"]) + 1
                block_f["F560"].append({"id_F560": ids["F560"], "id_F010": ids["F010"],
                                        "vl_rec_comp": parts[2], "cst_pis": parts[3],
                                        "vl_desc_pis": parts[4], "quant_bc_pis": parts[5],
                                        "aliq_pis_quant": parts[6], "vl_pis": parts[7],
                                        "cst_cofins": parts[8], "vl_desc_cofins": parts[9],
                                        "quant_bc_cofins": parts[10], "aliq_cofins_quant": parts[11],
                                        "vl_cofins": parts[12], "cod_mod": parts[13],
                                        "cfop": parts[14], "cod_cta": parts[15],
                                        "info_compl": parts[16]})
            elif registry == "F569" and ids["F560"]:
                ids["F569"] = len(block_f["F569"]) + 1
                block_f["F569"].append({"id_F569": ids["F569"], "id_F560": ids["F560"],
                                        "num_proc": parts[2], "ind_proc": parts[3]})
            elif registry == "F600" and ids["F010"]:
                ids["F600"] = len(block_f["F600"]) + 1
                block_f["F600"].append({"id_F600": ids["F600"], "id_F010": ids["F010"],
                                        "ind_nat_ret": parts[2], "dt_ret": parts[3],
                                        "vl_bc_ret": parts[4], "vl_ret": parts[5],
                                        "cod_rec": parts[6], "ind_nat_rec": parts[7],
                                        "cnpj": parts[8], "vl_ret_pis": parts[9],
                                        "vl_ret_cofins": parts[10], "ind_dec": parts[11]})
            elif registry == "F700" and ids["F010"]:
                ids["F700"] = len(block_f["F700"]) + 1
                block_f["F700"].append({"id_F700": ids["F700"], "id_F010": ids["F010"],
                                        "ind_ori_ded": parts[2], "ind_nat_ded": parts[3],
                                        "vl_ded_pis": parts[4], "vl_ded_cofins": parts[5],
                                        "vl_bc_oper": parts[6], "cnpj": parts[7],
                                        "inf_comp": parts[8]})
            elif registry == "F800" and ids["F010"]:
                ids["F800"] = len(block_f["F800"]) + 1
                block_f["F800"].append({"id_F800": ids["F800"], "id_F010": ids["F010"],
                                        "ind_nat_even": parts[2], "dt_even": parts[3],
                                        "cnpj_suced": parts[4], "pa_cont_cred": parts[5],
                                        "cod_cred": parts[6], "vl_cred_pis": parts[7],
                                        "vl_cred_cofins": parts[8], "per_cred_cis": parts[9]})
            elif registry == "F990" and ids["F001"]:
                ids["F990"] = len(block_f["F990"]) + 1
                block_f["F990"].append({"id_F990": ids["F990"], "id_F001": ids["F001"], "qtd_lin_f": parts[2]})

        return {reg: pd.DataFrame(table) for reg, table in block_f.items()}

    def parse_block_i(self, lines):
        """ Parse block I of a SPED file.
            Parameter:
            lines: list of strings.
            Returns a dictionary of DataFrame objects.
        """
        block_i = defaultdict(list)

        ids = {'I001': None,
               'I010': None,
               'I100': None,
               'I199': None,
               'I200': None,
               'I299': None,
               'I300': None,
               'I399': None,
               'I990': None}

        for line in lines:
            parts = line.strip().split("|")

            # Prevents index error when a file is malformed.
            if len(parts) < 2:
                continue

            registry = parts[1]

            if registry == "I001":
                ids["I001"] = len(block_i["I001"]) + 1
                block_i["I001"].append({"id_I001": ids["I001"], "ind_mov": parts[2]})
            if registry == "I010" and ids["I001"]:
                ids["I010"] = len(block_i["I010"]) + 1
                block_i["I010"].append({"id_I010": ids["I010"], "id_I001": ids["I001"],
                                        "cnpj": parts[2], "ind_ativ": parts[3],
                                        "info_compl": parts[4]})
            if registry == "I100" and ids["I010"]:
                ids["I100"] = len(block_i["I100"]) + 1
                block_i["I100"].append({"id_I100": ids["I100"], "id_I010": ids["I010"],
                                        "vl_rec": parts[2], "cst_pis_cofins": parts[3],
                                        "vl_tot_ded_ger": parts[4], "vl_tot_ded_esp": parts[5],
                                        "vl_bc_pis": parts[6], "aliq_pis": parts[7],
                                        "vl_pis": parts[8], "vl_bc_cofins": parts[9],
                                        "aliq_cofins": parts[10], "vl_cofins": parts[11],
                                        "info_compl": parts[12]})
            if registry == "I199" and ids["I100"]:
                ids["I199"] = len(block_i["I199"]) + 1
                block_i["I199"].append({"id_I199": ids["I199"], "id_I100": ids["I100"],
                                        "num_proc": parts[2], "ind_proc": parts[3]})
            if registry == "I200" and ids["I100"]:
                ids["I200"] = len(block_i["I200"]) + 1
                block_i["I200"].append({"id_I200": ids["I200"], "id_I100": ids["I100"],
                                        "num_campo": parts[2], "cod_det": parts[3],
                                        "det_valor": parts[4], "cod_cta": parts[5],
                                        "info_compl": parts[6]})
            if registry == "I299" and ids["I200"]:
                ids["I299"] = len(block_i["I299"]) + 1
                block_i["I299"].append({"id_I299": ids["I299"], "id_I200": ids["I200"],
                                        "num_proc": parts[2], "ind_proc": parts[3]})
            if registry == "I300" and ids["I001"]:
                ids["I300"] = len(block_i["I300"]) + 1
                block_i["I300"].append({"id_I300": ids["I300"], "id_I001": ids["I001"],
                                        "cod_comp": parts[2], "det_valor": parts[3],
                                        "cod_cta": parts[4], "info_compl": parts[5]})
            if registry == "I399" and ids["I300"]:
                ids["I399"] = len(block_i["I399"]) + 1
                block_i["I399"].append({"id_I399": ids["I399"], "id_I300": ids["I300"],
                                        "num_proc": parts[2], "ind_proc": parts[3]})
            elif registry == "I990" and ids["I001"]:
                ids["I990"] = len(block_i["I990"]) + 1
                block_i["I990"].append({"id_I990": ids["I990"], "id_I001": ids["I001"], "qtd_lin_i": parts[2]})

        return {reg: pd.DataFrame(table) for reg, table in block_i.items()}

    def parse_block_m(self, lines):
        """ Parse block M of a SPED file.
            Parameter:
            lines: list of strings.
            Returns a dictionary of DataFrame objects.
        """
        block_m = defaultdict(list)

        ids = {'M001': None,
               'M100': None,
               'M105': None,
               'M110': None,
               'M115': None,
               'M200': None,
               'M205': None,
               'M210': None,
               'M211': None,
               'M215': None,
               'M220': None,
               'M230': None,
               'M300': None,
               'M350': None,
               'M400': None,
               'M410': None,
               'M500': None,
               'M505': None,
               'M510': None,
               'M515': None,
               'M600': None,
               'M605': None,
               'M610': None,
               'M611': None,
               'M615': None,
               'M620': None,
               'M625': None,
               'M630': None,
               'M700': None,
               'M800': None,
               'M810': None,
               'M990': None}

        for line in lines:
            parts = line.strip().split("|")

            # Prevents index error when a file is malformed.
            if len(parts) < 2:
                continue

            registry = parts[1]

            if registry == "M001":
                ids["M001"] = len(block_m["M001"]) + 1
                block_m["M001"].append({"id_M001": ids["M001"], "ind_mov": parts[2]})
            if registry == "M100" and ids["M001"]:
                ids["M100"] = len(block_m["M100"]) + 1
                block_m["M100"].append({"id_M100": ids["M100"], "id_M001": ids["M001"],
                                        "cod_cred": parts[2],
                                        "ind_cred_ori": parts[3], "vl_bc_pis": parts[4],
                                        "aliq_pis": parts[5], "quant_bc_pis": parts[6],
                                        "aliq_pis_quant": parts[7], "vl_cred": parts[8],
                                        "vl_ajus_acres": parts[9], "vl_ajus_reduc": parts[10],
                                        "vl_cred_dif": parts[11], "vl_cred_disp": parts[12],
                                        "ind_desc_cred": parts[13], "vl_cred_desc": parts[14],
                                        "sld_cred": parts[15]})
            if registry == "M105" and ids["M100"]:
                ids["M105"] = len(block_m["M105"]) + 1
                block_m["M105"].append({"id_M105": ids["M105"], "id_M100": ids["M100"],
                                        "nat_bc_cred": parts[2],
                                        "cst_pis": parts[3], "vl_bc_pis_tot": parts[4],
                                        "vl_bc_pis_cum": parts[5], "vl_bc_pis_nc": parts[6],
                                        "vl_bc_pis": parts[7], "quant_bc_pis_tot": parts[8],
                                        "quant_bc_pis": parts[9], "desc_cred": parts[10]})
            if registry == "M110" and ids["M100"]:
                ids["M110"] = len(block_m["M110"]) + 1
                block_m["M110"].append({"id_M110": ids["M110"], "id_M100": ids["M100"],
                                        "ind_aj": parts[2], "vl_aj": parts[3],
                                        "cod_aj": parts[4], "num_doc": parts[5],
                                        "descr_aj": parts[6], "dt_ref": parts[7]})
            if registry == "M115" and ids["M110"]:
                ids["M115"] = len(block_m["M115"]) + 1
                block_m["M115"].append({"id_M115": ids["M115"], "id_M100": ids["M100"],
                                        "det_valor_aj": parts[2], "cst_pis": parts[3],
                                        "det_bc_cred": parts[4], "det_aliq": parts[5],
                                        "dt_oper_aj": parts[6], "desc_aj": parts[7],
                                        "cod_cta": parts[8], "info_compl": parts[9]})
            if registry == "M200" and ids["M001"]:
                ids["M200"] = len(block_m["M200"]) + 1
                block_m["M200"].append({"id_M200": ids["M200"], "id_M001": ids["M001"],
                                        "vl_tot_cont_nc_per": parts[2], "vl_tot_cred_desc": parts[3],
                                        "vl_tot_cred_desc_ant": parts[4], "vl_tot_cont_nc_dev": parts[5],
                                        "vl_ret_nc": parts[6], "vl_out_ded_nc": parts[7],
                                        "vl_count_nc_rec": parts[8], "vl_tot_count_cum_per": parts[9],
                                        "vl_ret_cum": parts[10], "vl_out_ded_cum": parts[11],
                                        "vl_count_cum_rec": parts[12], "vl_tot_cont_rec": parts[13]})
            if registry == "M205" and ids["M200"]:
                ids["M205"] = len(block_m["M205"]) + 1
                block_m["M205"].append({"id_M205": ids["M205"], "id_M200": ids["M200"],
                                        "num_campo": parts[2], "cod_rec": parts[3],
                                        "vl_debito": parts[4]})
            if registry == "M210" and ids["M200"]:
                ids["M210"] = len(block_m["M210"]) + 1
                block_m["M210"].append({"id_M210": ids["M210"], "id_M200": ids["M200"],
                                        "cod_cont": parts[2], "vl_rec_brt": parts[3],
                                        "vl_bc_cont": parts[4], "vl_ajus_acres_bc_pis": parts[5],
                                        "vl_ajus_reduc_bc_pis": parts[6], "vl_bc_cont_ajus": parts[7],
                                        "aliq_pis": parts[8], "quant_bc_pis": parts[9],
                                        "aliq_pis_quant": parts[10], "vl_cont_apur": parts[11],
                                        "vl_ajus_acres": parts[12], "vl_ajus_reduc": parts[13],
                                        "vl_cont_difer": parts[14], "vl_cont_difer_ant": parts[15],
                                        "vl_cont_per": parts[16]})
            if registry == "M211" and ids["M210"]:
                ids["M211"] = len(block_m["M211"]) + 1
                block_m["M211"].append({"id_M211": ids["M211"], "id_M210": ids["M210"],
                                        "ind_tip_coop": parts[2], "vl_bc_cont_ant_exc_coop": parts[3],
                                        "vl_exc_coop_ger": parts[4], "vl_exc_esp_coop": parts[5],
                                        "vl_bc_cont": parts[6]})
            if registry == "M215" and ids["M210"]:
                ids["M215"] = len(block_m["M215"]) + 1
                block_m["M215"].append({"id_M215": ids["M215"], "id_M210": ids["M210"],
                                        "ind_aj_bc": parts[2], "vl_aj_bc": parts[3],
                                        "cod_aj_bc": parts[4], "num_doc": parts[5],
                                        "descr_aj_bc": parts[6], "dt_ref": parts[7],
                                        "cod_cta": parts[8], "cnpj": parts[9],
                                        "info_compl": parts[10]})
            if registry == "M220" and ids["M200"]:
                ids["M220"] = len(block_m["M220"]) + 1
                block_m["M220"].append({"id_M220": ids["M220"], "id_M200": ids["M200"],
                                        "ind_aj": parts[2], "vl_aj": parts[3],
                                        "cod_aj": parts[4], "num_doc": parts[5],
                                        "descr_aj": parts[6], "dt_ref": parts[7]})
            if registry == "M225" and ids["M220"]:
                ids["M225"] = len(block_m["M225"]) + 1
                block_m["M225"].append({"id_M225": ids["M225"], "id_M220": ids["M220"],
                                       "det_valor_aj": parts[2], "cst_pis": parts[3],
                                        "det_bc_cred": parts[4], "det_aliq": parts[5],
                                        "dt_oper_aj": parts[6], "desc_aj": parts[7],
                                        "cod_cta": parts[8], "info_compl": parts[9]})
            if registry == "M230" and ids["M200"]:
                ids["M230"] = len(block_m["M230"]) + 1
                block_m["M230"].append({"id_M230": ids["M230"], "id_M200": ids["M200"],
                                        "cnpj": parts[2], "vl_vend": parts[3],
                                        "vl_nao_receb": parts[4], "vl_cont_dif": parts[5],
                                        "vl_cred_dif": parts[6], "cod_cred": parts[7]})
            if registry == "M300" and ids["M001"]:
                ids["M300"] = len(block_m["M300"]) + 1
                block_m["M300"].append({"id_M300": ids["M300"], "id_M001": ids["M001"],
                                        "cod_cont": parts[2], "vl_cont_apur_difer": parts[3],
                                        "nat_cred_desc": parts[4], "vl_cred_desc_difer": parts[5],
                                        "vl_cont_difer_ant": parts[6], "per_apur": parts[7], "dt_receb": parts[8]})
            if registry == "M350" and ids["M001"]:
                ids["M350"] = len(block_m["M350"]) + 1
                block_m["M350"].append({"id_M350": ids["M350"], "id_M001": ids["M001"],
                                        "vl_tot_fol": parts[2], "vl_exc_bc": parts[3],
                                        "vl_tot_bc": parts[4], "aliq_pis_fol": parts[5],
                                        "vl_tot_cont_fol": parts[6]})
            if registry == "M400" and ids["M001"]:
                ids["M400"] = len(block_m["M400"]) + 1
                block_m["M400"].append({"id_M400": ids["M400"], "id_M001": ids["M001"],
                                        "cst_pis": parts[2], "vl_tot_rec": parts[3],
                                        "cod_cta": parts[4], "desc_compl": parts[5]})
            if registry == "M410" and ids["M400"]:
                ids["M410"] = len(block_m["M410"]) + 1
                block_m["M410"].append({"id_M410": ids["M410"], "id_M400": ids["M400"],
                                        "nat_rec": parts[2], "vl_rec": parts[3],
                                        "cod_cta": parts[4], "desc_compl": parts[5]})
            if registry == "M500" and ids["M001"]:
                ids["M500"] = len(block_m["M500"]) + 1
                block_m["M500"].append({"id_M500": ids["M500"], "id_M001": ids["M001"],
                                        "cod_cred": parts[2], "ind_cred_ori": parts[3],
                                        "vl_bc_cofins": parts[4], "aliq_cofins": parts[5],
                                        "quant_bc_cofins": parts[6], "aliq_cofins_quant": parts[7],
                                        "vl_cred": parts[8], "vl_ajus_acres": parts[9],
                                        "vl_ajus_reduc": parts[10], "vl_cred_difer": parts[11],
                                        "vl_cred_disp": parts[12], "ind_desc_cred": parts[13],
                                        "vl_cred_desc": parts[14], "sld_cred": parts[15]})
            if registry == "M505" and ids["M500"]:
                ids["M505"] = len(block_m["M505"]) + 1
                block_m["M505"].append({"id_M505": ids["M505"], "id_M500": ids["M500"],
                                        "nat_bc_cred": parts[2], "cst_cofins": parts[3],
                                        "vl_bc_cofins_tot": parts[4], "vl_bc_cofins_cum": parts[5],
                                        "vl_bc_cofins_nc": parts[6], "vl_bc_cofins": parts[7],
                                        "quant_bc_cofins_tot": parts[8], "quant_bc_cofins": parts[9],
                                        "desc_cred": parts[10]})
            if registry == "M510" and ids["M500"]:
                ids["M510"] = len(block_m["M510"]) + 1
                block_m["M510"].append({"id_M510": ids["M510"], "id_M500": ids["M500"],
                                        "ind_aj": parts[2], "vl_aj": parts[3], "cod_aj": parts[4],
                                        "num_doc": parts[5], "descr_aj": parts[6], "dt_ref": parts[7]})
            if registry == "M515" and ids["M510"]:
                ids["M515"] = len(block_m["M515"]) + 1
                block_m["M515"].append({"id_M515": ids["M515"], "id_M510": ids["M510"],
                                        "det_valor_aj": parts[2], "cst_cofins": parts[3],
                                        "det_bc_cred": parts[4], "det_aliq": parts[5],
                                        "dt_oper_aj": parts[6], "desc_aj": parts[7],
                                        "cod_cta": parts[8], "info_compl": parts[9]})
            if registry == "M600" and ids["M001"]:
                ids["M600"] = len(block_m["M600"]) + 1
                block_m["M600"].append({"id_M600": ids["M600"], "id_M001": ids["M001"],
                                        "vl_tot_cont_nc_per": parts[2], "vl_tot_cred_desc": parts[3],
                                        "vl_tot_cred_desc_ant": parts[4], "vl_tot_cont_nc_dev": parts[5],
                                        "vl_ret_nc": parts[6], "vl_out_ded_nc": parts[7], "vl_cont_nv_rec": parts[8],
                                        "vl_tot_cont_cum_per": parts[9], "vl_ret_cum": parts[10],
                                        "vl_out_ded_cum": parts[11], "vl_cont_cum_rec": parts[12],
                                        "vl_tot_cont_rec": parts[13]})
            if registry == "M605" and ids["M600"]:
                ids["M605"] = len(block_m["M605"]) + 1
                block_m["M605"].append({"id_M605": ids["M605"], "id_M600": ids["M600"],
                                        "num_campo": parts[2], "cod_rec": parts[3],
                                        "vl_debito": parts[4]})
            if registry == "M610" and ids["M600"]:
                ids["M610"] = len(block_m["M610"]) + 1
                block_m["M610"].append({"id_M610": ids["M610"], "id_M600": ids["M600"],
                                        "cod_count": parts[2], "vl_rec_brt": parts[3],
                                        "vl_bc_cont": parts[4], "vl_ajus_acres_bc_cofins": parts[5],
                                        "vl_ajus_reduc_bc_cofins": parts[6], "vl_bc_cont_ajus": parts[7],
                                        "aliq_cofins": parts[8], "quant_bc_cofins": parts[9],
                                        "aliq_cofins_quant": parts[10], "vl_cont_apur": parts[11],
                                        "vl_ajus_acres": parts[12], "vl_ajus_reduc": parts[13],
                                        "vl_cont_difer": parts[14], "vl_cont_difer_ant": parts[15],
                                        "vl_cont_per": parts[16]})
            if registry == "M611" and ids["M600"]:
                ids["M611"] = len(block_m["M611"]) + 1
                block_m["M611"].append({"id_M611": ids["M611"], "id_M600": ids["M600"],
                                        "ind_tip_coop": parts[2], "vl_bc_cont_ant_exc_coop": parts[3],
                                        "vl_exc_coop_ger": parts[4], "vl_exc_esp_coop": parts[5],
                                        "vl_bc_cont": parts[6]})
            if registry == "M615" and ids["M600"]:
                ids["M615"] = len(block_m["M615"]) + 1
                block_m["M615"].append({"id_M615": ids["M615"], "id_M600": ids["M600"],
                                        "ind_aj_bc": parts[2], "vl_aj_bc": parts[3],
                                        "cod_aj_bc": parts[4], "num_doc": parts[5],
                                        "descr_aj_bc": parts[6], "dt_ref": parts[7],
                                        "cod_cta": parts[8], "cnpj": parts[9],
                                        "info_compl": parts[10]})
            if registry == "M620" and ids["M600"]:
                ids["M620"] = len(block_m["M620"]) + 1
                block_m["M620"].append({"id_M620": ids["M620"], "id_M600": ids["M600"],
                                        "ind_aj": parts[2], "vl_aj": parts[3], "cod_aj": parts[4],
                                        "num_doc": parts[5], "descr_aj": parts[6],
                                        "dt_ref": parts[7]}) 
            if registry == "M625" and ids["M620"]:
                ids["M625"] = len(block_m["M625"]) + 1
                block_m["M625"].append({"id_M625": ids["M625"], "id_M620": ids["M620"],
                                        "det_valor_aj": parts[2], "cst_cofins": parts[3],
                                        "det_bc_cred": parts[4], "det_aliq": parts[5],
                                        "dt_oper_aj": parts[6], "desc_aj": parts[7],
                                        "cod_cta": parts[8], "info_compl": parts[9]})
            if registry == "M630" and ids["M600"]:
                ids["M630"] = len(block_m["M630"]) + 1
                block_m["M630"].append({"id_M630": ids["M630"], "id_M600": ids["M600"],
                                        "cnpj": parts[2], "vl_vend": parts[3],
                                        "vl_nao_receb":  parts[4], "vl_cont_dif": parts[5],
                                        "vl_cred_dif": parts[6], "cod_cred": parts[7]})
            if registry == "M700" and ids["M001"]:
                ids["M700"] = len(block_m["M700"]) + 1
                block_m["M700"].append({"id_M700": ids["M700"], "id_M001": ids["M001"],
                                        "cod_cont": parts[2], "vl_cont_apur_difer": parts[3],
                                        "nat_cred_desc": parts[4], "vl_cred_desc_difer": parts[5],
                                        "vl_cont_difer_ant": parts[6], "per_apur": parts[7],
                                        "dt_receb": parts[8]})
            if registry == "M800" and ids["M001"]:
                ids["M800"] = len(block_m["M800"]) + 1
                block_m["M800"].append({"id_M800": ids["M800"], "id_M001": ids["M001"],
                                        "cst_cofins": parts[2], "vl_tot_rec": parts[3],
                                        "cod_cta": parts[4], "desc_compl": parts[5]})
            if registry == "M810" and ids["M800"]:
                ids["M810"] = len(block_m["M810"]) + 1
                block_m["M810"].append({"id_M810": ids["M810"], "id_M800": ids["M800"],
                                        "nat_rec": parts[2], "vl_rec": parts[3], "cod_cta": parts[4],
                                        "desc_compl": parts[5]})
            elif registry == "M990" and ids["M001"]:
                ids["M990"] = len(block_m["M990"]) + 1
                block_m["M990"].append({"id_M990": ids["M990"], "id_M001": ids["M001"], "qtd_lin_m": parts[2]})

        return {reg: pd.DataFrame(table) for reg, table in block_m.items()}

    def parse_block_p(self, lines):
        """ Parse block P of a SPED file.
            Parameter:
            lines: list of strings.
            Returns a dictionary of DataFrame objects.
        """
        block_p = defaultdict(list)

        ids = {'P001': None,
               'P010': None,
               'P100': None,
               'P110': None,
               'P199': None,
               'P200': None,
               'P210': None,
               'P990': None}

        for line in lines:
            parts = line.strip().split("|")

            # Prevents index error when a file is malformed.
            if len(parts) < 2:
                continue

            registry = parts[1]

            if registry == "P001":
                ids["P001"] = len(block_p["P001"]) + 1
                block_p["P001"].append({"id_P001": ids["P001"], "ind_mov": parts[2]})
            if registry == "P010" and ids["P001"]:
                ids["P010"] = len(block_p["P010"]) + 1
                block_p["P010"].append({"id_P010": ids["P010"], "cnpj": parts[2]})
            if registry == "P100" and ids["P010"]:
                ids["P100"] = len(block_p["P100"]) + 1
                block_p["P100"].append({"id_P100": ids["P100"], "id_P010": ids["P010"],
                                        "dt_ini": parts[2], "dt_fin": parts[3],
                                        "vl_rec_tot_est": parts[4], "cod_ativ_econ": parts[5],
                                        "vl_rec_ativ_estab": parts[6], "vl_exc": parts[7],
                                        "vl_bc_cont": parts[8], "aliq_cont": parts[9],
                                        "vl_cont_apu": parts[10], "cod_cta": parts[11],
                                        "info_compl": parts[12]})
            if registry == "P110" and ids["P100"]:
                ids["P110"] = len(block_p["P110"]) + 1
                block_p["P110"].append({"id_P110": ids["P110"], "id_P100": ids["P100"],
                                        "num_campo": parts[2], "cod_det": parts[3],
                                        "det_valor": parts[4], "inf_compl": parts[5]})
            if registry == "P199" and ids["P100"]:
                ids["P199"] = len(block_p["P199"]) + 1
                block_p["P199"].append({"id_P199": ids["P199"], "id_P100": ids["P100"],
                                        "num_proc": parts[2], "ind_proc": parts[3]})
            if registry == "P200" and ids["P010"]:
                ids["P200"] = len(block_p["P200"]) + 1
                block_p["P200"].append({"id_P200": ids["P200"], "id_P010": ids["P010"],
                                        "per_ref": parts[2], "vl_tot_cont_apu": parts[3],
                                        "vl_tot_aj_reduc": parts[4], "vl_tot_aj_acres": parts[5],
                                        "vl_tot_cont_dev": parts[6], "cod_rec": parts[7]}) 
            if registry == "P210" and ids["P200"]:
                ids["P210"] = len(block_p["P210"]) + 1
                block_p["P210"].append({"id_P210": ids["P210"], "id_P200": ids["P200"],
                                        "ind_aj": parts[2], "vl_aj": parts[3],
                                        "cod_aj": parts[4], "num_doc": parts[5],
                                        "descr_aj": parts[6], "dt_ref": parts[7]})
            elif registry == "P990" and ids["P001"]:
                ids["P990"] = len(block_p["P990"]) + 1
                block_p["P990"].append({"id_P990": ids["P990"], "id_P001": ids["P001"], "qtd_lin_p": parts[2]})

        return {reg: pd.DataFrame(table) for reg, table in block_p.items()}

    def parse_block_1(self, lines):
        """ Parse block 1 of a SPED file.
            Parameter:
            lines: list of strings.
            Returns a dictionary of DataFrame objects.
        """
        block_1 = defaultdict(list)

        ids = {'1001': None,
               '1010': None,
               '1011': None,
               '1020': None,
               '1050': None,
               '1100': None,
               '1101': None,
               '1102': None,
               '1200': None,
               '1210': None,
               '1220': None,
               '1300': None,
               '1500': None,
               '1501': None,
               '1502': None,
               '1600': None,
               '1610': None,
               '1620': None,
               '1700': None,
               '1800': None,
               '1809': None,
               '1900': None,
               '1990': None}

        for line in lines:
            parts = line.strip().split("|")

            # Prevents index error when a file is malformed.
            if len(parts) < 2:
                continue

            registry = parts[1]

            if registry == "1001":
                ids["1001"] = len(block_1["1001"]) + 1
                block_1["1001"].append({"id_1001": ids["1001"], "ind_mov": parts[2]})
            if registry == "1010" and ids["1001"]:
                ids["1010"] = len(block_1["1010"]) + 1
                block_1["1010"].append({"id_1010": ids["1010"], "id_1001": ids["1001"],
                                        "num_proc": parts[2], "id_sec_jud": parts[3], "id_vara": parts[4],
                                        "ind_nat_acao": parts[5], "desc_dec_jud": parts[6],
                                        "dt_sent_jud": parts[7]})
            if registry == "1011" and ids["1010"]:
                ids["1011"] = len(block_1["1011"]) + 1
                block_1["1011"].append({"id_1011": ids["1011"], "id_1010": ids["1010"],
                                        "reg_ref": parts[2],
                                        "chave_doc": parts[3], "cod_part": parts[4],
                                        "cod_item": parts[5], "dt_oper": parts[6],
                                        "vl_oper": parts[7], "cst_pis": parts[8],
                                        "vl_bc_pis": parts[9], "aliq_pis": parts[10],
                                        "vl_pis": parts[11], "cst_cofins": parts[12],
                                        "vl_bc_cofins": parts[13], "aliq_cofins": parts[14],
                                        "vl_cofins": parts[15], "cst_pis_susp": parts[16],
                                        "vl_bc_pis_susp": parts[17], "aliq_pis_susp": parts[18],
                                        "vl_pis_susp": parts[19], "cst_cofins_susp": parts[20],
                                        "vl_bc_cofins_susp": parts[21], "aliq_cofins_susp": parts[22],
                                        "vl_cofins_susp": parts[23], "cod_cta": parts[24],
                                        "cod_ccus": parts[25], "desc_doc_oper": parts[26]})
            if registry == "1020" and ids["1001"]:
                ids["1020"] = len(block_1["1020"]) + 1
                block_1["1020"].append({"id_1020": ids["1020"], "id_1001": ids["1001"],
                                        "num_proc": parts[2], "ind_nat_acao": parts[3],
                                        "dt_dec_adm": parts[4]})
            if registry == "1050" and ids["1001"]:
                ids["1050"] = len(block_1["1050"]) + 1
                block_1["1050"].append({"id_1050": ids["1050"], "id_1001": ids["1001"],
                                        "dt_ref": parts[2], "ind_aj_bc": parts[3],
                                        "cnpj": parts[4], "vl_aj_tot": parts[5],
                                        "vl_aj_cst01": parts[6], "vl_aj_cst02": parts[7],
                                        "vl_aj_cst03": parts[8], "vl_aj_cst04": parts[9],
                                        "vl_aj_cst05": parts[10], "vl_aj_cst06": parts[11],
                                        "vl_aj_cst07": parts[12], "vl_aj_cst08": parts[13],
                                        "vl_aj_cst09": parts[14], "vl_aj_cst49": parts[15],
                                        "vl_aj_cst99": parts[16], "ind_aprop": parts[17],
                                        "num_rec": parts[18], "info_compl": parts[19]})
            if registry == "1100" and ids["1001"]:
                ids["1100"] = len(block_1["1100"]) + 1
                block_1["1100"].append({"id_1100": ids["1100"], "id_1001": ids["1001"],
                                        "per_apu_cred": parts[2], "orig_cred": parts[3],
                                        "cnpj_suc": parts[4], "cod_cred": parts[5],
                                        "vl_cred_apu": parts[6], "vl_cred_ext_apu": parts[7],
                                        "vl_tot_cred_apu": parts[8], "vl_cred_desc_pa_ant": parts[9],
                                        "vl_cred_per_pa_ant": parts[10], "vl_cred_dcomp_pa_ant": parts[11],
                                        "sd_cred_disp_efd": parts[12], "vl_cred_desc_efd": parts[13],
                                        "vl_cred_per_efd": parts[14], "vl_cred_dcomp_efd": parts[15],
                                        "vl_cred_trans": parts[16], "vl_cred_out": parts[17],
                                        "sld_cred_fim": parts[18]})
            if registry == "1101" and ids["1100"]:
                ids["1101"] = len(block_1["1101"]) + 1
                block_1["1101"].append({"id_1101": ids["1101"], "id_1100": ids["1100"],
                                        "cod_part": parts[2], "cod_item": parts[3],
                                        "cod_mod": parts[4], "ser": parts[5],
                                        "sub_ser": parts[6], "num_doc": parts[7],
                                        "dt_oper": parts[8], "chv_nfe": parts[9],
                                        "vl_oper": parts[10], "cfop": parts[11],
                                        "nat_bc_cred": parts[12], "ind_orig_cred": parts[13],
                                        "cst_pis": parts[14], "vl_bc_pis": parts[15],
                                        "aliq_pis": parts[16], "vl_pis": parts[17],
                                        "cod_cta": parts[18], "cod_ccus": parts[19],
                                        "desc_compl": parts[20], "per_escrit": parts[21],
                                        "cnpj": parts[22]})
            if registry == "1102" and ids["1100"]:
                ids["1102"] = len(block_1["1102"]) + 1
                block_1["1102"].append({"id_1102": ids["1102"], "id_1100": ids["1100"],
                                        "vl_cred_pis_trib_mi": parts[2], "vl_cred_pis_nt_mi": parts[3],
                                        "vl_cred_pis_exp": parts[4]})
            if registry == "1200" and ids["1001"]:
                ids["1200"] = len(block_1["1200"]) + 1
                block_1["1200"].append({"id_1200": ids["1200"], "id_1001": ids["1001"],
                                        "per_apur_ant": parts[2], "nat_cont_rec": parts[3],
                                        "vl_cont_apur": parts[4], "vl_cred_pis_desc": parts[5],
                                        "vl_cont_dev": parts[6], "vl_out_ded": parts[7],
                                        "vl_cont_ext": parts[8], "vl_mul": parts[9],
                                        "vl_jur": parts[10], "dt_recol": parts[11]})
            if registry == "1210" and ids["1200"]:
                ids["1210"] = len(block_1["1210"]) + 1
                block_1["1210"].append({"id_1210": ids["1210"], "id_1200": ids["1200"],
                                        "cnpj": parts[2], "cst_pis": parts[3], "cod_part": parts[4],
                                        "dt_oper": parts[5], "vl_oper": parts[6],
                                        "vl_bc_pis": parts[7], "aliq_pis": parts[8],
                                        "vl_pis": parts[9], "cod_cta": parts[10],
                                        "desc_compl": parts[11]})
            if registry == "1220" and ids["1200"]:
                ids["1220"] = len(block_1["1220"]) + 1
                block_1["1220"].append({"id_1220": ids["1220"], "id_1200": ids["1200"],
                                        "per_apu_cred": parts[2], "orig_cred": parts[3],
                                        "cod_cred": parts[4], "vl_cred": parts[5]})
            if registry == "1300" and ids["1001"]:
                ids["1300"] = len(block_1["1300"]) + 1
                block_1["1300"].append({"id_1300": ids["1300"], "id_1001": ids["1001"],
                                        "ind_nat_ret": parts[2], "pr_rec_ret": parts[3],
                                        "vl_ret_apu": parts[4], "vl_ret_ded": parts[5],
                                        "vl_ret_per": parts[6], "vl_ret_dcomp": parts[7],
                                        "sld_ret": parts[8]})
            if registry == "1500" and ids["1001"]:
                ids["1500"] = len(block_1["1500"]) + 1
                block_1["1500"].append({"id_1500": ids["1500"], "id_1001": ids["1001"],
                                        "per_apu_cred": parts[2], "orig_cred": parts[3],
                                        "cnpj_suc": parts[4], "cod_cred": parts[5],
                                        "vl_cred_apu": parts[6], "vl_cred_ext_apu": parts[7],
                                        "vl_tot_cred_apu": parts[8], "vl_cred_desc_pa_ant": parts[9],
                                        "vl_cred_per_pa_ant": parts[10], "vl_cred_dcomp_pa_ant": parts[11],
                                        "sd_cred_disp_efd": parts[12], "vl_cred_desc_efd": parts[13],
                                        "vl_cred_per_efd": parts[14], "vl_cred_dcomp_efd": parts[15],
                                        "vl_cred_trans": parts[16], "vl_cred_out": parts[17],
                                        "sld_cred_fim": parts[18]})
            if registry == "1501" and ids["1500"]:
                ids["1501"] = len(block_1["1501"]) + 1
                block_1["1501"].append({"id_1501": ids["1501"], "id_1500": ids["1500"],
                                        "cod_part": parts[2], "cod_item": parts[3],
                                        "cod_mod": parts[4], "ser": parts[5],
                                        "sub_ser": parts[6], "num_doc": parts[7],
                                        "dt_oper": parts[8], "chv_nfe": parts[9],
                                        "vl_oper": parts[10], "cfop": parts[11],
                                        "nat_bc_cred": parts[12], "ind_orig_cred": parts[13],
                                        "cst_cofins": parts[14], "vl_bc_cofins": parts[15],
                                        "aliq_cofins": parts[16], "vl_cofins": parts[17],
                                        "cod_cta": parts[18], "cod_ccus": parts[19],
                                        "desc_compl": parts[20], "per_escrit": parts[21],
                                        "cnpj": parts[22]})
            if registry == "1502" and ids["1500"]:
                ids["1502"] = len(block_1["1502"]) + 1
                block_1["1502"].append({"id_1502": ids["1502"], "id_1500": ids["1500"],
                                        "vl_cred_cofins_trib_mi": parts[2],
                                        "vl_cred_cofins_nt_mi": parts[3],
                                        "vl_cred_cofins_exp": parts[4]})
            if registry == "1600" and ids["1001"]:
                ids["1600"] = len(block_1["1600"]) + 1
                block_1["1600"].append({"id_1600": ids["1600"], "id_1001": ids["1001"],
                                        "per_apur_ant": parts[2], "nat_cont_rec": parts[3],
                                        "vl_cont_apur": parts[4], "vl_cred_cofins_desc": parts[5],
                                        "vl_cont_dev": parts[6], "vl_out_ded": parts[7],
                                        "vl_cont_ext": parts[8], "vl_mul": parts[9],
                                        "vl_jur": parts[10], "dt_recol": parts[11]})
            if registry == "1610" and ids["1600"]:
                ids["1610"] = len(block_1["1610"]) + 1
                block_1["1610"].append({"id_1610": ids["1610"], "id_1600": ids["1600"],
                                        "cnpj": parts[2], "cst_cofins": parts[3],
                                        "cod_part": parts[4], "dt_oper": parts[5],
                                        "vl_oper": parts[6], "vl_bc_cofins": parts[7],
                                        "aliq_cofins": parts[8], "vl_cofins": parts[9],
                                        "cod_cta": parts[10], "desc_compl": parts[11]})
            if registry == "1620" and ids["1600"]:
                ids["1620"] = len(block_1["1620"]) + 1
                block_1["1620"].append({"id_1620": ids["1620"], "id_1600": ids["1600"],
                                        "per_apu_cred": parts[2], "orig_cred": parts[3],
                                        "cod_cred": parts[4], "vl_cred": parts[5]})
            if registry == "1700" and ids["1001"]:
                ids["1700"] = len(block_1["1700"]) + 1
                block_1["1700"].append({"id_1700": ids["1700"], "id_1001": ids["1001"],
                                        "ind_nat_ret": parts[2], "pr_rec_ret": parts[3],
                                        "vl_ret_apu": parts[4], "vl_ret_ded": parts[5],
                                        "vl_ret_per": parts[6], "vl_ret_dcomp": parts[7],
                                        "sld_ret": parts[8]})
            if registry == "1800" and ids["1001"]:
                ids["1800"] = len(block_1["1800"]) + 1
                block_1["1800"].append({"id_1800": ids["1800"], "id_1001": ids["1001"],
                                       "inc_imob": parts[2], "rec_receb_ret": parts[3],
                                        "rec_fin_ret": parts[4], "bc_ret": parts[5],
                                        "aliq_ret": parts[6], "vl_rec_uni": parts[7],
                                        "dt_rec_uni": parts[8], "cod_rec": parts[9]})
            if registry == "1809" and ids["1800"]:
                ids["1809"] = len(block_1["1809"]) + 1
                block_1["1809"].append({"id_1809": ids["1809"], "id_1800": ids["1800"],
                                        "num_proc": parts[2], "ind_proc": parts[3]})
            if registry == "1900" and ids["1001"]:
                ids["1900"] = len(block_1["1900"]) + 1
                block_1["1900"].append({"id_1900": ids["1900"], "id_1001": ids["1001"],
                                        "cnpj": parts[2], "cod_mod": parts[3],
                                        "ser": parts[4], "sub_ser": parts[5],
                                        "cod_sit": parts[6], "vl_tot_rec": parts[7],
                                        "quant_doc": parts[8], "cst_pis": parts[9],
                                        "cst_cofins": parts[10], "cfop": parts[11],
                                        "inf_compl": parts[12], "cod_cta": parts[13]})
            elif registry == "1990" and ids["1001"]:
                ids["1990"] = len(block_1["1990"]) + 1
                block_1["1990"].append({"id_1990": ids["1990"], "id_1001": ids["1001"], "qtd_lin_1": parts[2]})

        return {reg: pd.DataFrame(table) for reg, table in block_1.items()}

    def parse_block_9(self, lines):
        """ Parse block 9 of a SPED file.
            Parameter:
            lines: list of strings.
            Returns a dictionary of DataFrame objects.
        """
        block_9 = defaultdict(list)

        ids = {'9001': None,
               '9900': None,
               '9990': None,
               '9999': None}

        for line in lines:
            parts = line.strip().split("|")

            # Prevents index error when a file is malformed.
            if len(parts) < 2:
                continue

            registry = parts[1]

            if registry == "9001":
                ids["9001"] = len(block_9["9001"]) + 1
                block_9["9001"].append({"id_9001": ids["9001"], "ind_mov": parts[2]})
            if registry == "9900" and ids["9001"]:
                ids["9900"] = len(block_9["9900"]) + 1
                block_9["9900"].append({"id_9900": ids["9900"], "id_9001": ids["9001"],
                                        "reg_blc": parts[2], "qtd_reg_blc": parts[3]})
            elif registry == "9990" and ids["9001"]:
                ids["9990"] = len(block_9["9990"]) + 1
                block_9["9990"].append({"id_9990": ids["9990"], "id_9001": ids["9001"], "qtd_lin_9": parts[2]})
            elif registry == "9999":
                ids["9999"] = len(block_9["9999"]) + 1
                block_9["9999"].append({"id_9999": ids["9999"], "qtd_lin": parts[2]})

        return {reg: pd.DataFrame(table) for reg, table in block_9.items()}

    def read_sped(self):
        """ Loads a sped file into memory and parses it block by block. """
        sped = Sped()

        # Load file into memory.
        with open(self.file_path, 'r', encoding='latin-1') as fp:
            lines = fp.readlines()

        block_0 = self.parse_block_0(lines)
        block_0 = Block("Bloco 0", block_0)

        block_a = self.parse_block_a(lines)
        block_a = Block("Bloco A", block_a)

        block_c = self.parse_block_c(lines)
        block_c = Block("Bloco C", block_c)

        block_d = self.parse_block_d(lines)
        block_d = Block("Bloco D", block_d)

        block_f = self.parse_block_f(lines)
        block_f = Block("Bloco F", block_f)

        block_i = self.parse_block_i(lines)
        block_i = Block("Bloco I", block_i)

        block_m = self.parse_block_m(lines)
        block_m = Block("Bloco M", block_m)

        block_p = self.parse_block_p(lines)
        block_p = Block("Bloco P", block_p)

        block_1 = self.parse_block_1(lines)
        block_1 = Block("Bloco 1", block_1)

        block_9 = self.parse_block_9(lines)
        block_9 = Block("Bloco 9", block_9)

        sped.add_block(block_0)
        sped.add_block(block_a)
        sped.add_block(block_c)
        sped.add_block(block_d)
        sped.add_block(block_f)
        sped.add_block(block_i)
        sped.add_block(block_m)
        sped.add_block(block_p)
        sped.add_block(block_1)
        sped.add_block(block_9)

        return sped
