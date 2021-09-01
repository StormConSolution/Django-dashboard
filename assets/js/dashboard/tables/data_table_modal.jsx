import {orderFilters} from "../helpers/filters"
import {manageTableOrderFiltersWithOptions} from '../helpers/helpers'
import ReactDom from 'react-dom'
import React from 'react'
import Pagination from '../../components/Pagination'
import DataTableModalRows from "../../components/DataTableModalRows";

let optionsState = {}
let table = document.querySelector("#data-items")
let pagination = document.getElementById("data-table-modal-pagination");
export function createTable(page, options){

    optionsState = options
    manageTableOrderFiltersWithOptions(table, createTable, optionsState)
    let content = document.getElementById("data-table-modal-content");
    let pageSize = document.getElementById("data-table-modal-page-size").value

    document.getElementById("data-modal-table-csv").href = options.csvURL
    fetch(options.dataURL + `&page_size=${pageSize}&page=${page}` + "&" + orderFilters(table))
    .then((response) => response.json())
    .then((data) => {
        document.querySelector("#modal-select-all-data-items-label").innerHTML = `Select all ${data.total} data items`
        for (let element of data.data) {
            ReactDom.render(<DataTableModalRows data={data.data}/>, content)
        }

        let firstElement = data.pageSize * (data.currentPage - 1) + 1;
        let lastElement = firstElement + data.pageSize - 1;
        ReactDom.render(
            <Pagination
                firstElement={firstElement}
                lastElement={lastElement}
                totalElements={ data.total}
                totalPages={data.totalPages}
                currentPageNumber={data.currentPage}
                callBack={createTable}
                options={options}
                divElement={pagination}
            />,
            pagination
        )
        let checked = document.querySelector("#modal-select-all-data-items").checked
        toggleSelectAllDataItemsOnPage(checked)
    });
}


document.querySelector("#modal-select-all-data-items").addEventListener("click", (e)=>{
    let checked = e.currentTarget.checked
	document.querySelector("#select-all-modal-data-items").checked = checked;
    toggleSelectAllDataItemsOnPage(checked)
})


$("#edit-data-item-modal-save-and-close").click(function(e){
    let text = $("#edit-data-item-modal-text").val()
    let language = $("#edit-data-item-modal-language").val()
    let sentiment = $("#edit-data-item-modal-sentiment").val()
    let id = $("#edit-data-item-modal-id").val()
    let form = new FormData
    form.set("text", text)
    form.set("sentiment", sentiment)
    form.set("language", language)
    fetch(`/api/data-item/${id}/`,{
        credentials:"include",
        body:form,
        method:"POST",
    })
        .then(function(resp){
            if(resp.status === 200){
                location.reload()
            } else {
                alert("error editing data")
            }
        })
})


document.getElementById("data-table-modal-page-size").addEventListener("change",()=>{
    createTable(1, optionsState)
})


document.querySelector("#button-bulk-action").addEventListener("click", evt => {
    let ids = []
    let selectAllDataItems = document.querySelector("#modal-select-all-data-items").checked
    if(selectAllDataItems){
        fetch(optionsState.dataURL + "&all-ids=1")
            .then(response => response.json())
            .then(data => {
                for(let id of data.data.ids){
                    ids.push(id)
                }
                reanalyzeDataItems(ids)
            })
    } else {
        document.querySelectorAll("[data-role='checkbox-bulk-action']:checked").forEach(element =>{
            const dataItem = element.getAttribute("data-item-id")
            ids.push(dataItem)
        })
        reanalyzeDataItems(ids)
    }
})


function reanalyzeDataItems(ids){
    fetch(`/api/data-item/?data-items=${ids.join(",")}`, {
        method: "PUT",
        credentials: "include",
    }).then(resp => {
        if(resp.status !== 200){
            alert("Error re-analyzing data items")
        } else {
            location.reload()
        }
    })
}

/**
 * @function toggleSelectAllDataItemsOnPage
 * @param {bool} checked
 */
function toggleSelectAllDataItemsOnPage(checked){
    document.querySelectorAll("input[data-role='checkbox-bulk-action']").forEach((e)=>{
        if(checked){
            e.checked = true
        } else {
            e.checked = false
        }
    })
}


document.querySelector("#select-all-modal-data-items").addEventListener("click", (e)=>{
    let checked = e.currentTarget.checked
    toggleSelectAllDataItemsOnPage(checked)
})


let dataTableModalCloseButton = document.querySelector("#close-data-table-modal")
dataTableModalCloseButton.addEventListener("click", (e) => {
    dataTableModalContainer.style.display = 'none'
    document.querySelector("#word-cloud-modal-container").innerHTML = ""
})

