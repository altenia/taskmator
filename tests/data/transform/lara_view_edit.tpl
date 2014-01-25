<%
    import re

    # Convert underscore to camelCase
    under_pat = re.compile(r'_([a-z])')
    def underscore_to_camel(text):
        return under_pat.sub(lambda x: x.group(1).upper(), text)

    def get_singular(name, capitalize = True):
        retval = name
        if (name[len(name)-1] == 's'):
            retval = name[0:len(name)-1]
        if (capitalize):
            retval = retval.capitalize();
        return retval

    def is_fillable(field):
        if (field['type'] == 'auto'):
            return False
        return True
%>
% for entity_name, entity_def in model['entities'].iteritems():
<!-- app/views/${entity_name}/edit.blade.php -->

<div class="container">

<h1>Edit {{ $record->name }}</h1>

<!-- if there are creation errors, they will show here -->
{{ HTML::ul($errors->all()) }}

{{ Form::model($record, array('route' => array('${entity_name}.update', $record->id), 'method' => 'PUT')) }}

% for field in entity_def['fields']:
    % if is_fillable(field):
	<div class="form-group">
		{{ Form::label('${field["name"]}', '${field["name"].capitalize()}') }}
		{{ Form::text('${field["name"]}', null, array('class' => 'form-control')) }}
	</div>
	% endif
% endfor

	{{ Form::submit('Edit', array('class' => 'btn btn-primary')) }}

{{ Form::close() }}

</div> <!-- container -->

% endfor