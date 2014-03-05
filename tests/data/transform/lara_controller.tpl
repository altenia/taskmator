<%namespace name="common" file="/codegen_common.tpl"/><%
    import re

    def get_plural(name, capitalize = False):
        retval = name
        if (name[len(name)-1] != 's'):
            if (name[len(name)-1] == 'y'):
                name = name[:len(name)-1] + 'ie'
            retval = name + 's'
        if (capitalize):
            retval = retval.capitalize();
        return retval

    # Convert underscore to camelCase
    under_pat = re.compile(r'_([a-z])')
    def to_camelcase(text, capitalize=False, pluralize=False):
        retval = text
        if (pluralize):
            retval = get_plural(retval, capitalize)
        elif (capitalize):
            retval = retval.capitalize()
        return under_pat.sub(lambda x: x.group(1).upper(), retval)

    # Generate service method invocation code
    def service_call(name, method, pluralize=True):
        return '$this->' + to_camelcase(entity_name) + 'Service->' + method + to_camelcase(entity_name, True, pluralize);

%><?php
/**
 * Models from schema: ${ model['schema-name'] } version ${ model['version'] }
 * Code generated by ${params['TASK_TYPE_NAME']}
 *
 */


% for entity_name, entity_def in model['entities'].iteritems():
/**
 * Controller class that provides web access to ${common.to_camelcase(entity_name, True)} resource
 *
 * @todo: Add following line in app/routes.php
 * Route::resource('${entity_name}', '${common.to_camelcase(entity_name, True)}Controller');
 */
class ${common.to_camelcase(entity_name, True)}Controller extends \BaseController {

    // The service object
	protected $${common.to_camelcase(entity_name)}Service;

	protected $layout = 'layouts.master';

	/**
	 * Constructor
	 */
	public function __construct() {
        $this->${common.to_camelcase(entity_name)}Service = new Service\${common.to_camelcase(entity_name, True)}Service();
    }

	/**
	 * Display a listing of the resource.
	 *
	 * @return Response
	 */
	public function index()
	{
		$qparams = Input::except(array('page', self::PAGE_SIZE_PNAME, '_offset', '_limit'));
		$offset = Input::get('_offset', 0);
		$limit = Input::get('_limit', 20);
		$page_size = Input::get(self::PAGE_SIZE_PNAME, 20);

		$records = ${service_call(entity_name, 'paginate', True)}($qparams, $page_size);
		$count = ${service_call(entity_name, 'count', True)}($qparams);

        // $qparams is used by view to generate query string
		$qparams[self::PAGE_SIZE_PNAME] = $page_size;
		$this->layout->content = View::make('${entity_name}.index')
		    ->with('qparams', $qparams)
		    ->with('records', $records)
		    ->with('count', $count);
	}

	/**
	 * Show the form for creating a new resource.
	 *
	 * @return Response
	 */
	public function create()
	{
		$this->layout->content = View::make('${entity_name}.create');
	}

	/**
	 * Store a newly created resource in storage.
	 *
	 * @return Response
	 */
	public function store()
	{
		$data = Input::all();

		try {
            $record = ${service_call(entity_name, 'create', False)}($data);
            Session::flash('message', 'Successfully created!');
            return Redirect::to('${get_plural(entity_name)}');
        } catch (Services\ValidationException $ve) {
            return Redirect::to('${get_plural(entity_name)}/create')
                ->withErrors($ve->getObject());
                //->withInput(Input::except('password'));
        } catch (Exception $e) {
            return Redirect::to('${get_plural(entity_name)}/create')
                ->withErrors($e->getMessage());
                //->withInput(Input::except('password'));
        }
	}

	/**
	 * Display the specified resource.
	 *
	 * @param  int  $id
	 * @return Response
	 */
	public function show($id)
	{
		$record = ${service_call(entity_name, 'find', False)}($id);

		// show the view and pass the nerd to it
		$this->layout->content = View::make('${entity_name}.show')
			->with('record', $record);
	}

	/**
	 * Show the form for editing the specified resource.
	 *
	 * @param  int  $id
	 * @return Response
	 */
	public function edit($id)
	{
	    $record = ${service_call(entity_name, 'find', False)}($id);

		$this->layout->content = View::make('${entity_name}.edit')
		    ->with('record', $record);
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

        try {
            $record = ${service_call(entity_name, 'update', False)}($id, $data);

            // @todo: Redirect to proper URL
            Session::flash('message', 'Successfully updated!');
            return Redirect::to('${get_plural(entity_name)}');
        } catch (Services\ValidationException $ve) {
            return Redirect::to('${get_plural(entity_name)}/' . $id . '/edit')
                ->withErrors($ve->getObject());
                //->withInput(Input::except('password'));
        } catch (Exception $e) {
            return Redirect::to('${get_plural(entity_name)}/' . $id . '/edit')
                ->withErrors($e->getMessage());
                //->withInput(Input::except('password'));
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
		$success = ${service_call(entity_name, 'destroy', False)}($id);

		if ($success) {
            Session::flash('message', 'Successfully deleted!');
            return Redirect::to('${get_plural(entity_name)}');
        } else {
            Session::flash('message', 'Entry not found');
            return Redirect::to('${get_plural(entity_name)}');
        }
	}
}
% endfor
