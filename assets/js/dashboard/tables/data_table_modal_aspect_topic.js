import {getFilters} from "../helpers/filters"
import {createPagination} from './utils/utils'
export function createTable(page, options){
    let content = document.getElementById("data-table-modal-content");
    content.innerHTML = "";
    let pagination = document.getElementById("data-table-modal-pagination");
    pagination.innerHTML = ""
    let pageSize = document.getElementById("data-table-modal-page-size").value
    let filtersValues = getFilters() 
    document.getElementById("data-modal-table-csv").href = `/api/data-per-aspect-topic/${window.project_id}/?format=csv&` + new URLSearchParams({
        "aspect-label": encodeURIComponent(options.aspectLabel),
        "topic-label": encodeURIComponent(options.topicLabel),
        "sentiment": options.sentiment,
        "date-from": filtersValues.dateFrom,
        "date-to": filtersValues.dateTo,
        "languages": encodeURIComponent(filtersValues.languages),
        "sources": encodeURIComponent(filtersValues.sources),
        "sourcesID": filtersValues.sourcesID
    })
    fetch(`/api/data-per-aspect-topic/${window.project_id}/?` + new URLSearchParams({
        "aspect-label": encodeURIComponent(options.aspectLabel),
        "topic-label": encodeURIComponent(options.topicLabel),
        "page": page,
        "page-size": pageSize,
        "sentiment": options.sentiment,
        "date-from": filtersValues.dateFrom,
        "date-to": filtersValues.dateTo,
        "languages": encodeURIComponent(filtersValues.languages),
        "sources": encodeURIComponent(filtersValues.sources),
        "sourcesID": filtersValues.sourcesID
    }))
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
        <b>${element.sourceLabel}</b>
       </td>
       <td class="text-center">
        ${element.weightedScore.toFixed(4)}
       </td>
       <td class="text-center">
         ${element.sentimentValue.toFixed(4)}
       </td>
       <td class="text-center">
         <a href="#" class="info-button">${element.languageCode}</a>
       </td>
        `;
            tr.innerHTML = row;
            content.append(tr);
        }
        let firstElement = data.pageSize * (data.currentPage - 1) + 1;
        let lastElement = firstElement + data.pageSize - 1;
        createPagination(firstElement, lastElement, data.total, data.currentPage, data.totalPages, pagination, createTable, options);
    });
}