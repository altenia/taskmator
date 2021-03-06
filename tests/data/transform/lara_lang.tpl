<%
    import re

    # Convert underscore to camelCase
    def underscore_to_title(text):
        return text.replace('_', ' ').title();

%><?php
/**
 * Models from schema: ${ model['schema-name'] } version ${ model['version'] }
 * Code generated by ${params['TASK_TYPE_NAME']}
 *
 */

% for entity_name, entity_def in model['entities'].iteritems():
/**
 * @todo: Copy this file to app/lang/<lang>/${entity_name}.php
 * Modify the values accordingly
 */
return array(
% for field in entity_def['fields']:
    '${field['name']}' => '${underscore_to_title(field['name'])}',
% endfor
);
% endfor
