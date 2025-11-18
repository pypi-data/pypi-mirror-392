class NtgsConfig:
    def __init__(self):
        self.fold_config = {
            "structtype_column": "FoldType",
            "fold_text": "'Anticline','Syncline','Antiform','Synform','Monocline','Monoform','Neutral','Fold axis','Overturned syncline'",
            "description_column": "Desc",
            "synform_text": "FoldType",
            "foldname_column": "FoldName",
            "objectid_column": "OBJECTID",
            "tightness_column": "IntlimbAng",
            "axial_plane_dipdir_column": "AxPlDipDir",
            "axial_plane_dip_column": "AxPlDip",
        }

        self.fault_config = {
            "orientation_type": "dip direction",
            "structtype_column": "FaultType",
            "fault_text": "'Thrust','Reverse','Normal','Shear zone','Strike-slip','Thrust','Unknown'",
            "dip_null_value": "-999",
            "dipdir_flag": "num",
            "dipdir_column": "DipDir",
            "dip_column": "Dip",
            "dipestimate_column": "DipEstimate",
            "dipestimate_text": "'NORTH_EAST','NORTH',<rest of cardinals>,'NOT ACCESSED'",
            "displacement_column": "Displace",
            "displacement_text": "'1m-100m', '100m-1km', '1km-5km', '>5km'",
            "fault_length_column": "FaultLen",
            "fault_length_text": "Small (0-5km),Medium (5-30km),Large (30-100km),Regional (>100km),Unclassified",
            "name_column": "FaultName",
            "objectid_column": "OBJECTID",
        }

        self.geology_config = {
            "unitname_column": "Formation",
            "alt_unitname_column": "Formation",
            "group_column": "Group",
            "supergroup_column": "Supergroup",
            "description_column": "LithDescn1",
            "minage_column": "AgeMin",
            "maxage_column": "AgeMax",
            "rocktype_column": "LithClass",
            "alt_rocktype_column": "RockCat",
            "sill_text": "RockCat",
            "intrusive_text": "RockCat",
            "volcanic_text": "RockCat",
            "objectid_column": "OBJECTID",
            "ignore_lithology_codes": ["cover", "Unknown"],
        }

        self.structure_config = {
            "orientation_type": "dip direction",
            "dipdir_column": "DipDir",
            "dip_column": "Dip",
            "description_column": "FeatDesc",
            "bedding_text": "ObsType",
            "overturned_column": "Desc",
            "overturned_text": "overturned",
            "objectid_column": "OBJECTID",
        }

        self.config_map = {
            "geology": self.geology_config,
            "structure": self.structure_config,
            "fault": self.fault_config,
            "fold": self.fold_config,
        }

    def __getitem__(self, datatype):
        return self.config_map[datatype]
