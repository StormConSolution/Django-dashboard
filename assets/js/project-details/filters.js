let moreFiltersModal = document.querySelector("#more-filters-modal");
let openMoreFiltersModal = document.querySelector("#open-more-filters-modal");
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
