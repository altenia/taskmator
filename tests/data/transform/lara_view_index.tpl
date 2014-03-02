<%namespace name="common" file="/codegen_common.tpl"/><%

    def is_fillable(field):
        if (field['type'] == 'auto'):
            return False
        return True
%>
% for entity_name, entity_def in model['entities'].iteritems():
<!-- app/views/${entity_name}/index.blade.php -->

@section('content')
<div class="container">

<h1>All the records</h1>

<!-- will be used to show any messages -->
@if (Session::has('message'))
	<div class="alert alert-info">{{ Session::get('message') }}</div>
@endif

<table class="table table-striped table-bordered">
	<thead>
		<tr>
% for field in entity_def['fields']:
			<td>{{ Lang::get('${entity_name}.${field["name"]}') }}</td>
% endfor
		</tr>
	</thead>
	<tbody>
	@foreach($records as $key => $value)
		<tr>
% for field in entity_def['fields']:
			<td>{{ $value->${field['name']} }}</td>
% endfor

			<!-- we will also add show, edit, and delete buttons -->
			<td>

				<!-- delete the record (uses the destroy method DESTROY /${entity_name}/{id} -->
                {{ Form::open(array('url' => '${entity_name}/' . $value->sid, 'class' => 'pull-right')) }}
                    {{ Form::hidden('_method', 'DELETE') }}
                    {{ Form::submit('Delete', array('class' => 'btn btn-warning')) }}
                {{ Form::close() }}

				<!-- show the record (uses the show method found at GET /${entity_name}/{id} -->
				<!-- @todo: Make sure that the 'id' is the correct primary key column on '$value->sid' -->
				<a class="btn btn-small btn-success" href="{{ URL::to('${entity_name}/' . $value->sid) }}">Show this ${entity_name}</a>

				<!-- edit this record (uses the edit method found at GET /${entity_name}/{id}/edit -->
				<a class="btn btn-small btn-info" href="{{ URL::to('${entity_name}/' . $value->sid . '/edit') }}">Edit this ${entity_name}</a>

			</td>
		</tr>
	@endforeach
	</tbody>
</table>

</div> <!-- container -->
@show
% endfor