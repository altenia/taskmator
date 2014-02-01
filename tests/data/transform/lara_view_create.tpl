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

@section('content')
<div class="container">

<h1>Create New</h1>

<!-- if there are creation errors, they will show here -->
{{ HTML::ul($errors->all()) }}

// Make sure that the primaryKey column name is sid
{{ Form::open(array('url' => '${entity_name}', 'class' => 'form-horizontal')) }}

% for field in entity_def['fields']:
    % if is_fillable(field):
	<div class="form-group">
		{{ Form::label('${field["name"]}', Lang::get('${entity_name}.${field["name"]}'), array('class' => 'col-sm-2 control-label')) }}
		<div class="col-sm-10">
		    {{ Form::text('${field["name"]}', Input::old('${field["name"]}'), array('class' => 'form-control')) }}
		</div>
	</div>
	% endif
% endfor

	<div class="form-group">
    	<div class="col-sm-offset-2 col-sm-10">
	{{ Form::submit('Create', array('class' => 'btn btn-primary')) }}
	    </div>
	</div>

{{ Form::close() }}

</div> <!-- container -->
@show
% endfor