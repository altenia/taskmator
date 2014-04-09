<%namespace name="common" file="/codegen_common.tpl"/><%

    def is_fillable(field):
        if (field['type'] == 'auto'):
            return False
        return True
%>
% for entity_name, entity_def in model['entities'].iteritems():
<!-- app/views/${entity_name}/show.blade.php -->

@section('content')
<div class="container">

<!-- @todo: the field to be displayed as title -->

<h1>View {{ $record->sid }}</h1>

<dl class="dl-horizontal">
% for field in entity_def['fields']:
    % if is_fillable(field):
	<dt>{{ Lang::get('${entity_name}.${field["name"]}') }}</dt>
    <dd>{{ $record->${field["name"]} }}</dd>
	% endif
% endfor
</dl>

</div> <!-- container -->
@show
% endfor