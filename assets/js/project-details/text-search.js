import {createTable} from '../dashboard/tables/data_table_modal'
import {metadataFiltersURL, normalFiltersURL} from "../dashboard/helpers/filters";

let inputTextSearch = document.querySelector("#text-search")
let inputTextSearchBtn = document.querySelector("#text-search-btn")

function search() {
	let text = inputTextSearch.value
	let urlSearch = new URLSearchParams({"text-search":text})
	let options = {}
	options.csvURL =`/api/new-data/project/${window.project_id}/?format=csv&` + metadataFiltersURL()+ "&" + normalFiltersURL() + `&${urlSearch}`
	options.dataURL =`/api/new-data/project/${window.project_id}/?`+ metadataFiltersURL()+ "&" + normalFiltersURL() + `&${urlSearch}`
	document.querySelector("#data-table-modal").style.display = "block"
	createTable(1, options)
}

inputTextSearch.addEventListener('keyup', function (e) {
	e.preventDefault();
    if (e.key === 'Enter' || e.keyCode === 13) {
		search()
    }
});

inputTextSearchBtn.addEventListener('click', search);
