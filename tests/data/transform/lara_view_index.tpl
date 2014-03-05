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
            <td>Actions</td>
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

				<!-- show the record (uses the show method found at GET /${common.get_plural(entity_name)}/{id} -->
				<!-- @todo: Make sure that the 'id' is the correct primary key column on '$value->sid' -->
				<a class="btn btn-small btn-success" href="{{ URL::to('${common.get_plural(entity_name)}/' . $value->sid) }}">Show</a>

				<!-- edit this record (uses the edit method found at GET /${common.get_plural(entity_name)}/{id}/edit -->
				<a class="btn btn-small btn-info" href="{{ URL::to('${common.get_plural(entity_name)}/' . $value->sid . '/edit') }}">Edit</a>

				<!-- delete the record (uses the destroy method DESTROY /${common.get_plural(entity_name)}/{id} -->
                {{ Form::open(array('url' => '${common.get_plural(entity_name)}/' . $value->sid, 'class' => '')) }}
                    {{ Form::hidden('_method', 'DELETE') }}
                    {{ Form::submit('Delete', array('class' => 'btn btn-warning')) }}
                {{ Form::close() }}

			</td>
		</tr>
	@endforeach
	</tbody>
</table>

<div class="text-center">
    <div class="pagination">
<?php echo $records->appends($qparams)->links(); ?>
	</div>
</div>

</div> <!-- container -->
@show
% endfor