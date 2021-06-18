import {convertFiltersToURL, getMetadataFilters} from "../dashboard/helpers/filters"
import {updateProjectDetailsPage} from "../project-details"
let openMoreFiltersModal = document.querySelector("#open-more-filters-modal");
let applyMoreFilters = document.querySelector("#apply-more-filters")

function applyFilter(){
    let filters = getMetadataFilters()
    convertFiltersToURL(filters)
    updateProjectDetailsPage()
}
applyMoreFilters.addEventListener("click", ()=>{
    applyFilter()
    $("#more-filters-modal").modal("hide")
})
/*
document
    .querySelector("#close-more-filters-modal")
    .addEventListener("click", () => {
        moreFiltersModal.style.display = "none";
    });
 */
if (openMoreFiltersModal) {
    openMoreFiltersModal.addEventListener("click", () => {
        $("#more-filters-modal").modal()
    });
}