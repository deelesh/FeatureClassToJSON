import arcpy
import json
import codecs
import os


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "GISServiceTools"
        self.alias = "sample"

        # List of tool classes associated with this toolbox
        self.tools = [FeatureClassToJSON]


class FeatureClassToJSON(object):
    _JSON_INDENT_LEVEL = 1
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Feature Class to JSON"
        self.description = "Converts a feature class to a JSON file."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
    
        ##Input Feature Class Parameter
        param0 = arcpy.Parameter("input_feature_class", "Input Feature Class", "Input",
                                 "Feature Layer", "Required")
        param0.filter.list = ["Point"]
        
        ##Attributes to Export Parameter
        param1 = arcpy.Parameter("attributes_to_export", "Attributes to Export", "Input",
                                 "Field", "Optional", multiValue=True)
        param1.parameterDependencies = [param0.name]
        param1.filter.list = ["Short", "Long", "Single", "Double", "Text"]
        
        ##JSON Structure Parameter
        param2 = arcpy.Parameter("json_structure", "JSON Structure", "Input",
                                         "String", "Required")
        param2.filter.type = "ValueList"
        param2.filter.list = ["GP_FEATURE_RECORD_SET_LAYER", "NASERVER_LOCATIONS"]
        param2.value = "GP_FEATURE_RECORD_SET_LAYER"
        
        ##Output JSON File Parameter
        param3 = arcpy.Parameter("output_json_file", "Output JSON File", "Output",
                                 "File", "Required")
        param3.filter.list = ["json"]
        
        params = [param0, param1, param2, param3]
        
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        feature_class = parameters[0].valueAsText
        json_file_param = parameters[3]
        if feature_class and not json_file_param.altered:
            json_file = os.path.join(arcpy.env.scratchFolder, os.path.basename(feature_class) + ".json")
            json_file_param.value = json_file
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        input_feature_class = parameters[0].valueAsText
        param_value = parameters[1].valueAsText
        attributes_to_export = param_value.split(";") if param_value else None
        json_struct_type = parameters[2].valueAsText
        output_json_file = parameters[3].valueAsText
        class_params = (input_feature_class, attributes_to_export)
        if json_struct_type == "GP_FEATURE_RECORD_SET_LAYER":    
            feature_class_dict = GPFeatureRecordSetLayer(*class_params)
        else:
            feature_class_dict = NAServerLocations(*class_params)
        #write out the JSON file in utf-8 encoding
        with codecs.open(output_json_file, "wb","utf-8",buffering=0) as json_fp:
            json_indent_level = FeatureClassToJSON._JSON_INDENT_LEVEL
            if json_indent_level == 0:
                json.dump(feature_class_dict.asDict,json_fp, sort_keys=True)
            else:
                json.dump(feature_class_dict.asDict,json_fp, sort_keys=True, indent=json_indent_level)
        return

class JSONDict(object):
    '''Represent the feature class as a dict that can be serialized to JSON'''
    
    ##Mappings used by all instance methods.
    #Store a mapping of factory code to WKID for spatial references where factory code  is not same as WKID code.
    _latest_wkid_to_wkid = {3857: 102100}
    #Store a mapping of shape types return by describe and geometry type required by JSON feature objects
    _shape_type_to_geometry_type = {"Point" : "esriGeometryPoint"}
    
    def __init__(self, feature_class, attributes_to_export=None):
        self._feature_class = feature_class
        self._desc_fc = arcpy.Describe(self._feature_class)
        self._attributes_to_export = attributes_to_export
        self.hasZ = self._desc_fc.hasZ
        self.features = self._getFeatures()
        
    def _getSR(self):
        '''returns the spatial reference of the feature class as JSON dict'''
        sr_dict = {"wkid" : None}
        sr = self._desc_fc.spatialReference
        sr_factory_code = max((sr.pcsCode, sr.gcsCode))
        sr_wkid = sr_factory_code
        if sr_factory_code in JSONDict._latest_wkid_to_wkid:
            sr_wkid = JSONDict._latest_wkid_to_wkid[sr_factory_code]
        sr_dict["wkid"] = sr_wkid
        return sr_dict
    
    def _getFields(self):
        '''returns the fields to be exported from the feature class as JSON array of field dicts'''
        FIELD_DICT_KEYS = ("name","type","alias")
        fields_json = []
        
        #get a list of field objects that should be exported from the feature class
        fields = [f for f in self._desc_fc.fields if f.name in self._attributes_to_export]
        #For each field object, populate the fields_dict
        for field in fields:
            fields_dict = dict.fromkeys(FIELD_DICT_KEYS)
            fields_dict["name"] = field.name
            fields_dict["alias"] = field.aliasName
            fields_dict["type"] = "esriFieldType" + field.type
            fields_json.append(fields_dict)
        return fields_json
    
    def _getFeatures(self):
        '''Returns feature geometries and attributes as a JSON array of feature Dict'''
        feature_dict_keys = ["geometry"]
        features_json = []
        attributes_to_export = self._attributes_to_export
        #We atleast need shape information from search cursor
        search_cursor_fields = ["SHAPE@"]
        #Add the attributes to export as additional fields when getting the search cursor
        if attributes_to_export:
            search_cursor_fields += attributes_to_export
            feature_dict_keys.append("attributes")
        if self._desc_fc.shapeType == "Point":
            serialize_method = self._toJSONPoint
        with arcpy.da.SearchCursor(self._feature_class, search_cursor_fields) as cursor:
            for row in cursor:
                feature_dict = dict.fromkeys(feature_dict_keys)
                feature_dict["geometry"] = serialize_method(row[0])
                if attributes_to_export:
                    feature_dict["attributes"] = dict(zip(attributes_to_export,row[1:]))
                features_json.append(feature_dict)
        
        return features_json
    def _toJSONPoint(self,point):
        '''Converts an arcpy point geometry object to the JSON point geometry object'''
        #We may have a point with null shape.
        point_dict = {"x": None, "y": 0}
        if point:
            point = point.firstPoint
            point_dict["x"] = point.X 
            point_dict["y"] = point.Y
            if self._desc_fc.hasZ:
                point_dict["z"] = point.Z
        return point_dict
        
        
    @property
    def asDict(self):
        fc_dict = {k:v for k,v in vars(self).iteritems() if not k.startswith("_")}
        return fc_dict
        
class GPFeatureRecordSetLayer(JSONDict):
    '''returns the feature class and its attributes as a JSON structure that can used as input with GP tasks.'''
    
    def __init__(self, feature_class, attributes_to_export=None):
        JSONDict.__init__(self, feature_class, attributes_to_export)
        ##Properties for GP_FEATURE_RECORD_SET_LAYER are "geometryType", "hasZ", "hasM",
        ##"spatialReference", "fields","features"            
        self.spatialReference = self._getSR()
        self.hasM = self._desc_fc.hasM
        self.geometryType = JSONDict._shape_type_to_geometry_type[self._desc_fc.shapeType]
        if self._attributes_to_export:
            self.fields = self._getFields()
    
    def _toJSONPoint(self,point):
            '''Converts an arcpy point geometry object to the JSON point geometry object'''
            #get the basic point dict from the base class
            point_dict = JSONDict._toJSONPoint(self,point)
            #add the m value if feature class is m-aware.            
            if self._desc_fc.hasM:
                point_dict["m"] = point.M
            
            return point_dict    
        

class NAServerLocations(JSONDict):
    '''returns the feature class and its attributes as a JSON structure that can used as input with NAServer services.'''
    def __init__(self, feature_class, attributes_to_export=None):
        JSONDict.__init__(self, feature_class, attributes_to_export)
        #Properties for NASERVER_LOCATIONS are "features", "type", "hasZ", "doNotLocateOnRestrictedElements"
        self.type = "features"
        self.doNotLocateOnRestrictedElements = True
    def _toJSONPoint(self,point):
        '''Converts an arcpy point geometry object to the JSON point geometry object'''
        #get the basic point dict from the base class
        point_dict = JSONDict._toJSONPoint(self,point)
        #add the spatial reference to the dict.
        point_dict["spatialReference"] = self._getSR()
        return point_dict    