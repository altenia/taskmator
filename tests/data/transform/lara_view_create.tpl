<%namespace name="common" file="/codegen_common.tpl"/><%

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
{{ Form::open(array('url' => '${common.get_plural(entity_name)}', 'class' => 'form-horizontal')) }}

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