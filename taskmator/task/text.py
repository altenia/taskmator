__author__ = 'ysahn'

import logging
import json
import os
import glob
import collections

from mako.lookup import TemplateLookup
from mako.template import Template

from taskmator.task.core import Task


class TransformTask(Task):
    """
    Class that transform a json into code using a template
    Uses mako as template engine for transformation
    """

    logger = logging.getLogger(__name__)

    ATTR_TEMPLATE_DIR = u'template_dir'
    ATTR_TEMPLATES = u'templates'
    ATTR_SRC_DIR = u'src_dir'
    ATTR_SRC_FILES = u'src_files'
    ATTR_DEST_DIR = u'dest_dir'
    ATTR_FILE_PREFIX = u'file_prefix'
    ATTR_FILE_EXT = u'file_ext'

    __VALID_ATTRS = [ATTR_TEMPLATE_DIR, ATTR_TEMPLATES, ATTR_SRC_DIR, ATTR_SRC_FILES,
                     ATTR_DEST_DIR, ATTR_FILE_PREFIX, ATTR_FILE_EXT]

    def __init__(self, name, parent=None):
        """
        Constructor
        """
        super(TransformTask, self).__init__(name, parent)
        self.template_dir = None
        self.templates = collections.OrderedDict()

    def setAttribute(self, attrKey, attrVal):
        if (attrKey in self.__VALID_ATTRS):
            self.attribs[attrKey] = attrVal
        else:
            super(TransformTask, self).setAttribute(attrKey, attrVal)

    def init(self):
        super(TransformTask, self).init()
        template_dir = self._normalize_dir(self.getAttribute(self.ATTR_TEMPLATE_DIR, './'), './')

        template_names = self.getAttribute(self.ATTR_TEMPLATES)
        if not template_names:
            raise ("Attribute '" + self.ATTR_TEMPLATES + "' is required")

        if (isinstance(template_names, basestring)):
            template_names = [template_names]

        tpl_lookup = TemplateLookup(directories=[template_dir])

        for template_name in template_names:
            template_paths = glob.glob(template_dir + template_name + '.tpl')
            for template_path in template_paths:
                atemplate = Template(filename=template_path, lookup=tpl_lookup)
                self.templates[template_path] = atemplate


    def executeInternal(self, execution_context):
        """
        @type execution_context: ExecutionContext
        """
        self.logger.info("Executing " + str(self))

        src_dir = self._normalize_dir(self.getAttribute(self.ATTR_SRC_DIR, './'), './')
        file_patterns = self.getAttribute(self.ATTR_SRC_FILES, '*.json')
        file_patterns = file_patterns if file_patterns else '*.json'

        # Convert to an array
        if (isinstance(file_patterns, basestring)):
            file_patterns = [file_patterns]
        outputs = {}
        for file_pattern in file_patterns:
            file_paths = glob.glob(src_dir + file_pattern)
            for file_path in file_paths:
                model = self._load_model(file_path)
                fname = self._get_filaname(file_path, False)
                for tpl_path, tpl in self.templates.iteritems():
                    tpl_name = self._get_filaname(tpl_path, False)
                    outputs[fname + '.' + tpl_name] = self._transform(tpl, model, self.getParams())

        # write to a file
        dest_dir = self._normalize_dir(self.getAttribute(self.ATTR_DEST_DIR, './'), './')
        file_ext = '.' + self.getAttribute(self.ATTR_FILE_EXT)
        for name, output in outputs.iteritems():
            self._write(output, dest_dir + name + file_ext)

        return (Task.CODE_OK, outputs)


    # Private methods
    def _normalize_dir(self, dir, default):
        dir = dir if dir else default
        dir = dir if dir.startswith('/') else os.getcwd() + '/' + dir
        return dir if dir.endswith('/') else dir + '/'

    def _load_model(self, model_uri):
        file = open(model_uri, "r")
        file_content = file.read()
        model = json.loads(file_content, object_pairs_hook=collections.OrderedDict)
        return model

    def _transform(self, thetemplate, model, params):
        return thetemplate.render_unicode(model=model, params=params)

    def _get_filaname(self, file_path, include_ext = True):
        """
        Returns the filename
        @param file_path: string     The path
        @param include_ext: boolean  Whether or not to include extension
        @return: string
        """
        retval = file_path
        last_sep_pos = file_path.rfind('/')
        if (last_sep_pos > -1):
            retval = file_path[last_sep_pos+1:]

        if (not include_ext):
            last_dot_pos = retval.rfind('.')
            if (last_dot_pos > -1):
                retval = retval[:last_dot_pos]

        return retval

    def _write(self, data, dest_path):
        self._normalize_dir(dest_path, './')
        with open(dest_path, "w") as text_file:
            text_file.write(data)
