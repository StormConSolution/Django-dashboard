export function createPagination(firstElement, lastElement, totalElements, currentPage, totalPages, paginationContainer, callBack){
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
    
    let page = 5
    if(totalPages < 5){
        page = totalPages
    }
    for(let i = 1; i < page; i++){
        let li = createPageNumber(currentPage, i, callBack)
        
        ulPagination.append(li)
    }


    if(totalPages == 5){
        let li = createPageNumber(currentPage, 5, callBack)
        ulPagination.append(li)
    }

    if(totalPages > 6){
        let li = document.createElement("li")
        let a = document.createElement("a")
        a.innerHTML = ".."
        li.append(a);
        ulPagination.append(li)
        li = createPageNumber(currentPage, totalPages, callBack)
        ulPagination.append(li)
    }

    paginationContainer.append(paginationDiv);
}

function createPageNumber(currentPageNumber, pageNumber, callBack){
    let li = document.createElement("li")
    let a = document.createElement("a")
    a.innerHTML = pageNumber
    a.setAttribute("style", "cursor:pointer")
    a.addEventListener("click", (e)=>{
        callBack(pageNumber)
    })
    if(currentPageNumber == pageNumber){
        li.className = "active"
    }
    li.append(a);
    return li
}