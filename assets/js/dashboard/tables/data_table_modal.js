import {getFilters, orderFilters} from "../helpers/filters"
import {manageTableOrderFiltersWithOptions} from '../helpers/helpers'
import {createPagination} from './utils/utils'
let optionsState = {}

let table = document.querySelector("#data-items")
export function createTable(page, options){
    optionsState = options
    manageTableOrderFiltersWithOptions(table, createTable, optionsState)
    let content = document.getElementById("data-table-modal-content");
    content.innerHTML = "";
    let pagination = document.getElementById("data-table-modal-pagination");
    pagination.innerHTML = ""
    let pageSize = document.getElementById("data-table-modal-page-size").value
    //document.getElementById("data-modal-table-csv").href = options.wordCloudURL
    document.getElementById("data-modal-table-csv").href = options.csvURL
    fetch(options.dataURL + `&page-size=${pageSize}&page=${page}` + "&" + orderFilters(table))
    .then((response) => response.json())
    .then((data) => {
        for (let element of data.data) {
            let tr = document.createElement("tr");
            var length = 150;
            let text = "";
            if(element.text.length > length){
                text = element.text.substring(0, length) + "...";
            } else {
                text = element.text
            }
            let row = `
        <td>
        <small>${element.dateCreated}</small>
       </td>
       <td>
         ${text}
       </td>
       <td >
        <b><a href="${element.url}">${element.sourceLabel}</a></b>
       </td>
       <td class="text-center">
         ${element.sentimentValue.toFixed(4)}
       </td>
       <td class="text-center">
         <a href="#" class="info-button">${element.languageCode}</a>
       </td>
       <td class="text-center">
        <a
            class="icon-link"
            data-toggle="tooltip"
            data-role="edit-data-item"
            data-placement="bottom"
            title="Edit"
            data-item-id="${element.id}"
        >
            <i class="fe fe-edit"></i>
        </a>
        <a
            class="icon-link"
            data-toggle="tooltip"
            data-role="refresh-data-item"
            data-placement="bottom"
            data-item-id="${element.id}"
            title="Re-analyze"
        >
            <i class="fe fe-refresh-cw"></i>
        </a>
        <a
            class="icon-link"
            data-toggle="tooltip"
            data-role="delete-data-item"
            data-placement="bottom"
            data-item-id="${element.id}"
            title="Delete"
        >
            <i class="fe fe-trash-2"></i>
        </a>
        </td>
        `;
            tr.innerHTML = row;
            content.append(tr);
        }
        let firstElement = data.pageSize * (data.currentPage - 1) + 1;
        let lastElement = firstElement + data.pageSize - 1;
        createPagination(firstElement, lastElement, data.total, data.currentPage, data.totalPages, pagination, createTable, options);
        document.querySelectorAll("[data-role='delete-data-item']")
        .forEach(element=> {
            element.addEventListener("click", (e)=>{
                let target = e.currentTarget
                let dataID = target.getAttribute("data-item-id")
                fetch(`/api/data-item/${dataID}/`, {
                    method:"DELETE",
                    credentials:"include"
                })
                .then(response =>{
                    if(response.status == 200){
                    location.reload()
                    }
                })
            })
        })
        document.querySelectorAll("[data-role='refresh-data-item']")
        .forEach(element=> {
            element.addEventListener("click", (e)=>{
                let target = e.currentTarget
                let dataID = target.getAttribute("data-item-id")
                fetch(`/api/data-item/${dataID}/`, {
                    method:"PUT",
                    credentials:"include"
                })
                .then(response =>{
                    if(response.status == 200){
                    location.reload()
                    //$("#close-data-table-modal").trigger('click')
                    //$("#data-table-modal").css("display", "block")
                    //createTable(page, optionsState)
                    }
                })
            })
        })
        document.querySelectorAll("[data-role='edit-data-item']")
        .forEach(element=> {
            element.addEventListener("click", (e)=>{
                let target = e.currentTarget
                let dataID = target.getAttribute("data-item-id")
                fetch(`/api/data-item/${dataID}/`, {credentials:"include"})
                .then(resp => resp.json())
                .then(data => {
                    $("#edit-data-item-modal-text").val(data.text)
                    $("#edit-data-item-modal-id").val(data.id)
                    $("#edit-data-item-modal-sentiment").val(data.sentiment)
                    $("#edit-data-item-modal-language").val(data.language)
                    $("#edit-data-item-modal").modal()
                })
            })
        })
        $("#edit-data-item-modal-save-and-close").click(function(e){
            var text = $("#edit-data-item-modal-text").val()
            var language = $("#edit-data-item-modal-language").val()
            var sentiment = $("#edit-data-item-modal-sentiment").val()
            var id = $("#edit-data-item-modal-id").val()
            var form = new FormData
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
    });
}

document.getElementById("data-table-modal-page-size").addEventListener("change",()=>{
    createTable(1, optionsState)
})
