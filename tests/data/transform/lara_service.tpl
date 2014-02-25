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

    # Camel and capitalize
    def name_for_suffix(name, singular=True):
        namex = name
        if (singular):
            namex = get_singular(name);
        return underscore_to_camel(namex).capitalize();

%><?php
/**
 * Models from schema: ${ model['schema-name'] } version ${ model['version'] }
 * Code generated by ${params['TASK_TYPE_NAME']}
 *
 */


% for entity_name, entity_def in model['entities'].iteritems():
/**
 * Service class that provides business logic for ${get_singular(entity_name, True)}
 */
class ${get_singular(entity_name, True)}Service extends \BaseService {

	/**
	 * Returns list of the records.
	 *
	 * @param array $queryParams  Parameters used for querying
	 * @param int   $offset       The starting record
	 * @param int   $limit        Maximum number of records to retrieve
	 * @return Response
	 */
	public function list${name_for_suffix(entity_name, False)}($queryParams, $offset = 0, $limit=100)
	{
		$records = \${get_singular(entity_name, True)}::all();
		return $records;
	}

	/**
	 * Creates a new records.
	 * Mostly wrapper around insert with pre and post processing.
	 *
	 * @param array $data  Parameters used for creating a new record
	 * @return mixed  null if successful, validation object validation fails
	 */
	public function create${name_for_suffix(entity_name)}($data)
	{

		$validator = \${get_singular(entity_name, True)}::validator($data);
        if ($validator->passes()) {
            $record = new \${get_singular(entity_name, True)}();
            $record->fill($data);

            /*
             * @todo: assign default values as needed
             */
            $now = new \DateTime;
            $now_str = $now->format('Y-m-d H:i:s');
            $record->uuid = uniqid();
            $record->created_dt = $now_str;
            $record->updated_dt = $now_str;
            $record->save();
            return null;
        } else {
            // Redirecting to same form
            return $validator;
        }
	}

	/**
	 * Retrieves a single record.
	 *
	 * @param  int $id  The primary key for the search
	 * @return ${get_singular(entity_name, True)}
	 */
	public function find${name_for_suffix(entity_name)}($id)
	{
		$record = \${get_singular(entity_name, True)}::find($id);

		return $record;
	}

	/**
	 * Update the specified resource in storage.
	 *
	 * @param  int   $id    The primary key of the record to update
	 * @param  array $data  The data of the update
	 * @return mixed null if successful, validation if validation error
	 */
	public function update${name_for_suffix(entity_name)}($id, $data)
	{
		$validator = \${get_singular(entity_name, True)}::validator($data);
        if ($validator->passes()) {
            $record = \${get_singular(entity_name, True)}::find($id);
            $record->fill($data);

            $now = new \DateTime;
            $now_str = $now->format('Y-m-d H:i:s');
            $record->updated_dt = $now_str;
            $record->save();
            return null;
        } else {
            return $validator;
        }
	}

	/**
	 * Remove the specified resource from storage.
	 *
	 * @param  int  $id
	 * @return bool true if deleted, false otherwise
	 */
	public function destroy${name_for_suffix(entity_name)}($id)
	{
		// delete
		$record = \${get_singular(entity_name, True)}::find($id);
		if (!empty($record)) {
		    $record->delete();
		    return true;
		}
		return false;

	}
}
% endfor
