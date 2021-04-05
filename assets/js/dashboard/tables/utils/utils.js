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
    
    if(totalPages < 7){
        for(let i = 0; i < totalPages; i++){
            let li = createPageNumber(currentPage, i, callBack)
            ulPagination.append(li) 
        }
    } else {
        let li = createPageNumber(currentPage, 1, callBack)
        ulPagination.append(li) 

        if(currentPage < 4){
            for(let i = 2; i < 5; i++){
                let li = createPageNumber(currentPage, i, callBack)
                ulPagination.append(li) 
            }
            let li = document.createElement("li")
            let a = document.createElement("a")
            a.innerHTML = ".."
            li.append(a);
            ulPagination.append(li)
            li = createPageNumber(currentPage, totalPages, callBack)
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
                    let li = createPageNumber(currentPage, i, callBack)
                    ulPagination.append(li) 
                }
                li = document.createElement("li")
                a = document.createElement("a")
                a.innerHTML = ".."
                li.append(a);
                ulPagination.append(li)
                li = createPageNumber(currentPage, totalPages, callBack)
                ulPagination.append(li)
            } else {
                for(let i = currentPage - 1; i <= totalPages; i++){
                    let li = createPageNumber(currentPage, i, callBack)
                    ulPagination.append(li)  
                }
            }
 
        }
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
