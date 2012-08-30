'''Unit test for tools in WebServiceTools toolbox.'''

import unittest
import os
import sys
import arcpy
import testutils

class TestFeatureClassToJSON(unittest.TestCase):
    '''Test cases for Feature Class to JSON tool.'''

    @classmethod
    def setUpClass(self):
        '''This method is called only once for all test cases.'''
        self.cwd = sys.path[0]
        self.base = os.path.join(self.cwd, "base")
        self.out = os.path.join(self.cwd, "out")
        if not os.path.exists(self.out):
            os.mkdir(self.out)
        tbx = os.path.join(os.path.dirname(self.cwd), "WebServiceTools.pyt")
        #do not import using an alias as the PYT already sets an alias
        arcpy.ImportToolbox(tbx)
        arcpy.env.overwriteOutput = True
        self.input_file_gdb = os.path.join(self.cwd, "TestInputs.gdb")

    def setUp(self):
        #register the custom file comparator so that it is called when we use assertEqual
        self.addTypeEqualityFunc(testutils.FileObject, testutils.assertFileEqual)

    def test_2DPointFCAndAttributesAsGP(self):
        '''Serialize attributes and geometries from a 2D point feature class in web mercator spatial reference as GPFeatureRecordSetLayer. '''

        input_fc_name = "CandidateStores_WebM"
        json_file_name = "{0}_GP.json".format(input_fc_name)

        #excute the tool
        input_fc = os.path.join(self.input_file_gdb, input_fc_name)
        export_attributes = ["Name"]
        json_struct_type = "GP_FEATURE_RECORD_SET_LAYER"
        output_json_file = os.path.join(self.out, json_file_name)
        result = arcpy.FeatureClassToJSON_sample(input_fc, export_attributes, json_struct_type, output_json_file)

        #Check if the execution succeeded without any warnings
        self.assertEqual(result.maxSeverity,0, result.getMessages())

        #Check if the output JSON file has expected contents
        base_json_file = testutils.FileObject(os.path.join(self.base, json_file_name))
        output_json_file = testutils.FileObject(output_json_file)
        self.assertEqual(base_json_file, output_json_file)

    def test_2DPointFCAsGP(self):
        '''Serialize geometries from a 2D point feature class in WGS84 spatial reference as GPFeatureRecordSetLayer. '''

        input_fc_name = "CandidateStores_WGS84"
        json_file_name = "{0}_GP.json".format(input_fc_name)

        #excute the tool
        input_fc = os.path.join(self.input_file_gdb, input_fc_name)
        export_attributes = None
        json_struct_type = "GP_FEATURE_RECORD_SET_LAYER"
        output_json_file = os.path.join(self.out, json_file_name)
        result = arcpy.FeatureClassToJSON_sample(input_fc, export_attributes, json_struct_type, output_json_file)

        #Check if the execution succeeded without any warnings
        self.assertEqual(result.maxSeverity,0, result.getMessages())

        #Check if the output JSON file has expected contents
        base_json_file = testutils.FileObject(os.path.join(self.base, json_file_name))
        output_json_file = testutils.FileObject(output_json_file)
        self.assertEqual(base_json_file, output_json_file)

    def test_2DPointFCAndAttributesAsNA(self):
        '''Serialize attributes and geometries from a 2D point feature class in web mercator spatial reference as NAServerLocations. '''

        input_fc_name = "CandidateStores_WebM"
        json_file_name = "{0}_NA.json".format(input_fc_name)

        #excute the tool
        input_fc = os.path.join(self.input_file_gdb, input_fc_name)
        export_attributes = ["Name"]
        json_struct_type = "NASERVER_LOCATIONS"
        output_json_file = os.path.join(self.out, json_file_name)
        result = arcpy.FeatureClassToJSON_sample(input_fc, export_attributes, json_struct_type, output_json_file)

        #Check if the execution succeeded without any warnings
        self.assertEqual(result.maxSeverity,0, result.getMessages())

        #Check if the output JSON file has expected contents
        base_json_file = testutils.FileObject(os.path.join(self.base, json_file_name))
        output_json_file = testutils.FileObject(output_json_file)
        self.assertEqual(base_json_file, output_json_file)    

    def test_2DPointFCAsNA(self):
        '''Serialize geometries from a 2D point feature class in WGS84 spatial reference as NAServerLocations. '''

        input_fc_name = "CandidateStores_WGS84"
        json_file_name = "{0}_NA.json".format(input_fc_name)

        #excute the tool
        input_fc = os.path.join(self.input_file_gdb, input_fc_name)
        export_attributes = None
        json_struct_type = "NASERVER_LOCATIONS"
        output_json_file = os.path.join(self.out, json_file_name)
        result = arcpy.FeatureClassToJSON_sample(input_fc, export_attributes, json_struct_type, output_json_file)

        #Check if the execution succeeded without any warnings
        self.assertEqual(result.maxSeverity,0, result.getMessages())

        #Check if the output JSON file has expected contents
        base_json_file = testutils.FileObject(os.path.join(self.base, json_file_name))
        output_json_file = testutils.FileObject(output_json_file)
        self.assertEqual(base_json_file, output_json_file)

if __name__ == '__main__':
    unittest.main(verbosity=1)