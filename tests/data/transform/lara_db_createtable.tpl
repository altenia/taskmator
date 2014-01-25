<%
    def get_type(field):
        type = field['type']
        if (type == 'auto'):
            return 'increments'
        elif (type == 'int'):
            return 'integer'
        elif (type == 'long'):
            return 'bigInteger'
        elif (type == 'datetime'):
            return 'dateTime'
        endif
        return field['type']

    def get_length(field):
        if ('length' in field):
            return ', ' + str(field['length'])
        return ''

    def get_modifiers(field):
        modifs = []
        if ('is_nullable' in field and field['is_nullable']):
            modifs.append('->nullable()')
        if ('is_unique' in field and field['is_unique']):
            modifs.append('->unique()')
        if ('default' in field):
            modifs.append('->default(\''+ field['default'] + '\')')

        return ''.join(modifs)

    def get_constraint(constr):
        return constr['kind']

    def get_constraint_param(constr):
        if (constr['kind'] == 'foreign'):
            return constr['key']
        else:
            return constr['field']

    def get_constraint_modifiers(constr):
        if (constr['kind'] != 'foreign'):
            return ''
        retval = '->references(\'' + constr['reference'] +'\')' + '->on(\'' + constr['on'] +'\')'

        return retval

%><?php
# Migration for schema: ${ model['schema-name'] }
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Database\Migrations\Migration;

% for entity_name, entity_def in model['entities'].iteritems():
class Create${entity_name.capitalize()}Table extends Migration {

	/**
	 * Run the migrations.
	 *
	 * @return void
	 */
	public function up()
	{
		Schema::create('${entity_name}', function(Blueprint $table)
		{
% for field in entity_def['fields']:
			$table->${get_type(field)}('${field["name"]}'${get_length(field)})${get_modifiers(field)};
% endfor
% if ('constraints' in entity_def):
% for constr in entity_def['constraints']:
		    $table->${get_constraint(constr)}('${get_constraint_param(constr)}')${get_constraint_modifiers(constr)};
% endfor
% endif
		});
	}

	/**
	 * Reverse the migrations.
	 *
	 * @return void
	 */
	public function down()
	{
		Schema::table('${entity_name}', function(Blueprint $table)
		{
			//
		});
	}

}
% endfor
