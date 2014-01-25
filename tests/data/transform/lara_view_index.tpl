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

<nav class="navbar navbar-inverse">
	<div class="navbar-header">
		<a class="navbar-brand" href="{{ URL::to('nerds') }}">Nerd Alert</a>
	</div>
	<ul class="nav navbar-nav">
		<li><a href="{{ URL::to('nerds') }}">View All Nerds</a></li>
		<li><a href="{{ URL::to('nerds/create') }}">Create a Nerd</a>
	</ul>
</nav>

<h1>All the records</h1>

<!-- will be used to show any messages -->
@if (Session::has('message'))
	<div class="alert alert-info">{{ Session::get('message') }}</div>
@endif

<table class="table table-striped table-bordered">
	<thead>
		<tr>
% for field in entity_def['fields']:
			<td>${field["name"].capitalize()}</td>
% endfor
		</tr>
	</thead>
	<tbody>
	@foreach($record as $key => $value)
		<tr>
% for field in entity_def['fields']:
			<td>{{ $value->id }}</td>
% endfor

			<!-- we will also add show, edit, and delete buttons -->
			<td>

				<!-- delete the record (uses the destroy method DESTROY /nerds/{id} -->
				<!-- we will add this later since its a little more complicated than the other two buttons -->

				<!-- show the record (uses the show method found at GET /nerds/{id} -->
				<a class="btn btn-small btn-success" href="{{ URL::to('nerds/' . $value->id) }}">Show this Nerd</a>

				<!-- edit this nerd (uses the edit method found at GET /nerds/{id}/edit -->
				<a class="btn btn-small btn-info" href="{{ URL::to('nerds/' . $value->id . '/edit') }}">Edit this Nerd</a>

			</td>
		</tr>
	@endforeach
	</tbody>
</table>

</div> <!-- container -->

% endfor