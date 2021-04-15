import {createPagination} from './utils/utils'
import {createTable as dataModalTable} from './data_table_modal_aspect_topic'
import {getFilters} from '../helpers/filters'
import {update, createHTMLForGraphsContainer as createHTML, createHTMLForGraphsContainer} from '../helpers/helpers'
export function createTable(page){
    update.startUpdate()
    makeTable(page)
}

let html = 
`
<div class="col-12 project-card">
<div class="project-card-inner">
  <div class="chart-title align-items-center d-flex flex-wrap">
    <h4 class="col p-0">Aspect Topic Breakdown <a href="#" data-toggle="tooltip" data-placement="top" title="Need help?">
        <i class="fe fe-help-circle"></i>
      </a> </h4>
    <div class="col-auto p-0 d-flex flex-wrap ">
    <div class="per-page align-items-center d-flex">
      Show <select class="custom-select" id="aspect-topic-table-page-size">
        <option value="10" selected>10</option>
        <option value="20">20</option>
        <option value="30">30</option>
        <option value="40">40</option>
      </select> Entries
    </div>
    <div class="data-search">
      <input type="text" class="form-control " placeholder="Search">
    </div>
    <a style="margin-left:1rem;display:flex;align-items:center;cursor:pointer;" id="aspect-topic-table-csv" target="_blank">Download CSV</a>
    </div>
  </div>
  <div class="data-table table-responsive">
    <table class="table table-striped table-borderless">
      <thead>
        <tr>
          <th scope="col">
            TOPIC <span class="data-short">
              <a href="#" class="active">
                <i class="fe fe-chevron-up"></i>
              </a>
              <a href="#">
                <i class="fe fe-chevron-down"></i>
              </a>
            </span>
          </th>
          <th scope="col">
            ASPECT <span class="data-short">
              <a href="#">
                <i class="fe fe-chevron-up"></i>
              </a>
              <a href="#">
                <i class="fe fe-chevron-down"></i>
              </a>
            </span>
          </th>
          <th scope="col" class="width-150 text-center">
            POSITIVES 
          </th>
          <th scope="col" class="width-150 text-center">
            NEGATIVES 
          </th>
        </tr>
      </thead>
      <tbody id="aspect-topic-table-content">
      </tbody>
    </table>
  </div>
  <div class="table-bottom" id="aspect-topic-table-pagination">
  </div>
</div>
</div>
`
function makeTable(page){
    createHTML(html)
    let content = document.getElementById("aspect-topic-table-content");
    content.innerHTML = "Loading...";
    let pagination = document.getElementById("aspect-topic-table-pagination");
    let pageSize = document.getElementById("aspect-topic-table-page-size").value
    pagination.innerHTML = ""
    let filtersValues = getFilters() 
    let urlParams = new URLSearchParams({
        "date-from": filtersValues.dateFrom,
        "date-to": filtersValues.dateTo,
        "languages": filtersValues.languages,
        "sources": filtersValues.sources
    })
    document.getElementById("aspect-topic-table-csv").href= `/api/aspect-topic/project/${window.project_id}/?format=csv&` + urlParams
    fetch(`/api/aspect-topic/project/${window.project_id}/?page=${page}&page-size=${pageSize}&` + urlParams)
    .then((response) => response.json())
    .then((data) => {
        content.innerHTML = ""
        for (let element of data.data) {
            let tr = document.createElement("tr");
            let row = `
            <td>
            <a href="#" class="data-link">${element.topicLabel}</a>
           </td>
           <td>
             ${element.aspectLabel}
           </td>
           <td class="text-center">
            <a style="cursor:pointer" class="info-button green" data-aspect="${element.aspectLabel}" data-topic="${element.topicLabel}" data-sentiment="positive">${element.positivesCount}</a>
           </td>
           <td class="text-center">
            <a style="cursor:pointer" class="info-button red" data-aspect="${element.aspectLabel}" data-topic="${element.topicLabel}" data-sentiment="negative">${element.negativesCount}</a>
           </td>
            `;
                tr.innerHTML = row;
                content.append(tr);

            }
            let buttons =content.querySelectorAll("a[data-topic]")
            for(let button of buttons){
                button.addEventListener("click", (e)=>{
                    let dataAspectLabel = e.target.getAttribute("data-aspect")
                    let dataTopicLabel = e.target.getAttribute("data-topic")
                    let sentiment = e.target.getAttribute("data-sentiment")
                    document.querySelector("#data-table-modal").style.display = "block"
                    dataModalTable(1, dataAspectLabel, dataTopicLabel, sentiment)
                })
            }
            let firstElement = data.pageSize * (data.currentPage - 1);
            let lastElement = firstElement + data.pageSize;
            createPagination(firstElement, lastElement, data.total, data.currentPage, data.totalPages, pagination, createTable);
            update.finishUpdate()
    });
}