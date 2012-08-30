'''Helper classes and functions for writing unit tests'''

import filecmp
import difflib
import codecs
import os


class FileObject(object):
    '''Class is used to convert a string file path to a new type so that it can be used with custom assertEqual calls'''
    
    def __init__(self, file_path):
        self.name = file_path
         
def assertFileEqual(base_file, test_file, msg=None):
    '''Compares two files and returns a boolean indicating their equality. If the files are not equal, the
    comparator writes all differences to a HTML file in the same folder as test_file. The arguments can be the file paths
    or the FileObject. 
    To use in a unit test register this function as typeEqualityFunc for custom FileObject type for example  
    def setUp(self):
        #register the custom file comparator so that it is called when we use assertEqual
        self.addTypeEqualityFunc(shared_utils.FileObject, shared_utils.assertFileEqual)    
    def test_myTest(self):
        #run test that produces a file as output
        #get a FileObject for the base file.
        #compare
        self.assertEqual(testFileObject, baseFileObject)
        '''
    if hasattr(base_file,"name"):
        base_file = base_file.name
    if hasattr(test_file, "name"):
        test_file = test_file.name
    if not os.path.exists(base_file):
        #raise self.failureException("Base file {0} does not exist.".format(base_file))
        raise AssertionError("Base file {0} does not exist.".format(base_file))
    if not os.path.exists(test_file):
        raise AssertionError("Output file {0} does not exist.".format(test_file))
    output_diff_file_name = "{0}_diff.html".format(os.path.splitext(os.path.basename(test_file))[0]) 
    output_diff_file = os.path.join(os.path.dirname(test_file), output_diff_file_name)
    
    #Check if the files are different
    is_equal = filecmp.cmp(base_file, test_file, shallow=False)
    #If equal, return
    if is_equal:
        return is_equal
    
    #Report the differences if files are not equal
    #Read all the contents from the two files as list of strings
    #Memory hungry approach. Research a better way if possible.        
    with codecs.open(test_file, "rb", 'utf-8', buffering=0) as test_file_fp:
        test_file_data = test_file_fp.readlines()
    with codecs.open(base_file, "rb", 'utf-8', buffering=0) as base_file_fp:
        base_file_data = base_file_fp.readlines()        
    
    #Set the column width to 80 so that we can see diffs from both files without scrolling.
    diff = difflib.HtmlDiff(wrapcolumn=80)
    #context is based on whether the file contents are same or different.
    #if file contents are same, using context=True produces the diff file with "no differences found" text.
    #If file contents are different, using context=False produces all the lines from the two files and not 
    #just the diff lines with some before and after lines
    diff_file_data = diff.make_file(test_file_data, base_file_data, test_file, base_file, context=is_equal)
    with codecs.open(output_diff_file, "wb", "utf-8", buffering=0) as output_diff_file_fp:
        output_diff_file_fp.write(diff_file_data)
    if not is_equal:
        raise AssertionError("Files are not equal. Check {0} for differences".format(output_diff_file))