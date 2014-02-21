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

    def service_call(name, method, singular=True):
        return '$this->' + get_singular(entity_name, False) + 'Service->' + method + name_for_suffix(entity_name, singular);

%><?php
/**
 * Models from schema: ${ model['schema-name'] } version ${ model['version'] }
 * Code generated by ${params['TASK_TYPE_NAME']}
 *
 */


% for entity_name, entity_def in model['entities'].iteritems():
/**
 * Add following line in app/routes.php
 * Route::resource('${entity_name}', '${get_singular(entity_name, True)}Controller');
 */
class ${get_singular(entity_name, True)}Controller extends \BaseController {

	protected $${get_singular(entity_name, False)}Service;

	/**
	 * Constructor
	 */
	public function __construct() {
        $this->${get_singular(entity_name, False)}Service = new Services\${get_singular(entity_name, True)}Service();
    }

	/**
	 * Display a listing of the resource.
	 *
	 * @return Response
	 */
	public function index()
	{
		$records = ${service_call(entity_name, 'list', False)}();
		return $list;
	}

	/**
	 * Showing the form is not supported
	 *
	 */
	public function create()
	{
		App::abort(404);
	}

	/**
	 * Store a newly created resource in storage.
	 *
	 * @return Response
	 */
	public function store()
	{
		$data = Input::all();

		$validation = ${service_call(entity_name, 'create', True)}($data);

        if (empty($validation)) {
            return Response::json(array(
                'error' => false),
                200
            );
        } else {
             return $validator->messages()->toJson();
        }
	}

	/**
	 * Return JSON representation of the specified resource.
	 *
	 * @param  int  $id
	 * @return Response
	 */
	public function show($id)
	{
		$record = ${service_call(entity_name, 'get', True)}($id);

		return $record;
	}

	/**
	 * Showing the form is not supported in API.
	 *
	 * @param  int  $id
	 * @return Response
	 */
	public function edit($id)
	{
	    App::abort(404);
	}

	/**
	 * Update the specified resource in storage.
	 *
	 * @param  int  $id
	 * @return Response
	 */
	public function update($id)
	{
		$data = Input::all();
		$validation = ${service_call(entity_name, 'update', True)}($id, $data);

        if (empty($validation)) {
            return Response::json(array(
                'error' => false),
                200
            );
        } else {
             return $validator->messages()->toJson();
        }
	}

	/**
	 * Remove the specified resource from storage.
	 *
	 * @param  int  $id
	 * @return Response
	 */
	public function destroy($id)
	{
		// delete
		$result = ${service_call(entity_name, 'update', True)}($id, $data);

		if ($result) {
		    return Response::json(array(
                'error' => false),
                200
            );
		} else {
		    App::abort(404);
		}
	}
}
% endfor