import {getFilters} from "../helpers/filters"
export function createTable(page, aspectLabel, topicLabel, sentiment){
    let content = document.getElementById("data-table-modal-content");
    content.innerHTML = "";
    let pagination = document.getElementById("data-table-modal-pagination");
    pagination.innerHTML = ""
    let pageSize = document.getElementById("data-table-modal-page-size").value
    let filtersValues = getFilters() 
    fetch(`/api/data-per-aspect-topic/${window.project_id}/?` + new URLSearchParams({
        "aspect-label": encodeURIComponent(aspectLabel),
        "topic-label": encodeURIComponent(topicLabel),
        "page": page,
        "page-size": pageSize,
        "sentiment": sentiment,
        "date-from": filtersValues.dateFrom,
        "date-to": filtersValues.dateTo,
        "languages": encodeURIComponent(filtersValues.languages),
        "sources": encodeURIComponent(filtersValues.sources)
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
        let firstElement = data.pageSize * (data.currentPage - 1);
        let lastElement = firstElement + data.pageSize;
        createPagination(firstElement, lastElement, data.total, data.currentPage, data.totalPages, pagination, createTable, aspectLabel, topicLabel, sentiment);
    });
}

function createPagination(firstElement, lastElement, totalElements, currentPage, totalPages, paginationContainer, callBack, aspectLabel, topicLabel, sentiment){
    let paginationDiv = document.createElement("div")
    paginationDiv.className = "row no-gutters"
    let paginationHtml = `
    <div class="col-12 col-md">
        <div class="pagination-data">Showing ${firstElement} to ${lastElement} of ${totalElements} entries</div>
    </div>
    `;

    paginationDiv.innerHTML = paginationHtml;

    let paginationNumbers = document.createElement("div")
    paginationNumbers.className = "col-12 col-md-auto";
    let ulPagination = document.createElement("ul")
    ulPagination.className="pagination"
    paginationNumbers.append(ulPagination)
    paginationDiv.append(paginationNumbers)
    
    if(totalPages < 7){
        for(let i = 0; i < totalPages; i++){
            let li = createPageNumber(currentPage, i, callBack,  aspectLabel, topicLabel, sentiment)
            ulPagination.append(li) 
        }
    } else {
        let li = createPageNumber(currentPage, 1, callBack, aspectLabel, topicLabel, sentiment)
        ulPagination.append(li) 

        if(currentPage < 4){
            for(let i = 2; i < 5; i++){
                let li = createPageNumber(currentPage, i, callBack, aspectLabel, topicLabel, sentiment)
                ulPagination.append(li) 
            }
            let li = document.createElement("li")
            let a = document.createElement("a")
            a.innerHTML = ".."
            li.append(a);
            ulPagination.append(li)
            li = createPageNumber(currentPage, totalPages, callBack, aspectLabel, topicLabel, sentiment)
            ulPagination.append(li) 
        }

        if(currentPage >= 4){
            li = document.createElement("li")
            let a = document.createElement("a")
            a.innerHTML = ".."
            li.append(a);
            ulPagination.append(li)
            if(currentPage < totalPages - 3){
                for(let i = currentPage - 1; i < currentPage +2; i++){
                    let li = createPageNumber(currentPage, i, callBack, aspectLabel, topicLabel, sentiment)
                    ulPagination.append(li) 
                }
                li = document.createElement("li")
                a = document.createElement("a")
                a.innerHTML = ".."
                li.append(a);
                ulPagination.append(li)
                li = createPageNumber(currentPage, totalPages, callBack, aspectLabel, topicLabel, sentiment)
                ulPagination.append(li)
            } else {
                for(let i = currentPage - 1; i <= totalPages; i++){
                    let li = createPageNumber(currentPage, i, callBack, aspectLabel, topicLabel, sentiment)
                    ulPagination.append(li)  
                }
            }
 
        }
    }

    paginationContainer.append(paginationDiv);
}

function createPageNumber(currentPageNumber, pageNumber, callBack, aspectLabel, topicLabel, sentiment){
    let li = document.createElement("li")
    let a = document.createElement("a")
    a.innerHTML = pageNumber
    a.setAttribute("style", "cursor:pointer")
    a.addEventListener("click", (e)=>{
        callBack(pageNumber, aspectLabel, topicLabel, sentiment)
    })
    if(currentPageNumber == pageNumber){
        li.className = "active"
    }
    li.append(a);
    return li
}