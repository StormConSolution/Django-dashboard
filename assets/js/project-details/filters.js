import {convertFiltersToURL, getMetadataFilters} from "../dashboard/helpers/filters"
import {updateProjectDetailsPage} from "../project-details"
let openMoreFiltersModal = document.querySelector("#open-more-filters-modal");
let applyMoreFilters = document.querySelector("#apply-more-filters")

function applyFilter(){
    let filters = getMetadataFilters()
    convertFiltersToURL(filters)
    updateProjectDetailsPage()
}

applyMoreFilters.addEventListener("click", (e)=>{
    applyFilter()
	let openFilterBtn = document.getElementById('open-more-filters-modal')
	openFilterBtn.classList.remove('btn-secondary');
	openFilterBtn.classList.add('btn-info');

	let resetBtn = document.getElementById('reset-filters')
	resetBtn.classList.remove('d-none')
    $("#more-filters-modal").modal("hide")
})

if (openMoreFiltersModal) {
    openMoreFiltersModal.addEventListener("click", (e) => {
        $("#more-filters-modal").modal()
    });
}
