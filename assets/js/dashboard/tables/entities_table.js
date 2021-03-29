import {createPagination} from './utils/utils'

function createTable(page){
    let content = document.getElementById("entity-table-content");
    content.innerHTML = "";
    let pagination = document.getElementById("entity-table-pagination");
    pagination.innerHTML = ""
    let pageSize = document.getElementById("aspect-topic-table-page-size").value
    fetch(`/api/entity/project/${window.project_id}/?page=${page}&page-size=${pageSize}`)
    .then((response) => response.json())
    .then((data) => {
        for (let element of data.data) {
            let tr = document.createElement("tr");
            let row = `
        <td>
        <a href="#" class="data-link">${element.entityLabel}</a>
       </td>
       <td>
         ${element.classificationLabel}
       </td>
       <td class="text-center">
        <a href="#" class="info-button">${element.count}</a>
       </td>
        `;
            tr.innerHTML = row;
            content.append(tr);
        }
        let firstElement = data.pageSize * (data.currentPage - 1);
        let lastElement = firstElement + data.pageSize;
        createPagination(firstElement, lastElement, data.total, data.currentPage, data.totalPages, pagination, createTable);
    });
}
createTable(1);