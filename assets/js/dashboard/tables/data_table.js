import {createPagination} from './utils/utils'
import {getFilters} from "../helpers/filters"
import {update, createHTMLForGraphsContainer as createHTML} from '../helpers/helpers'
let html = 
`
<div class="col-12 project-card">
<div class="project-card-inner">
  <div class="chart-title align-items-center d-flex flex-wrap">
    <h4 class="col p-0">Data Items <a href="#" data-toggle="tooltip" data-placement="top" title="Need help?">
        <i class="fe fe-help-circle"></i>
      </a> </h4>
    <div class="col-auto p-0 d-flex flex-wrap ">
    <div class="per-page align-items-center d-flex">
      Show <select class="custom-select" id="data-table-page-size">
        <option value="10" selected>10</option>
        <option value="20">20</option>
        <option value="30">30</option>
        <option value="40">40</option>
      </select> Entries
    </div>
    <div class="data-search">
      <input type="text" class="form-control " placeholder="Search">
    </div>
    <a style="margin-left:1rem;display:flex;align-items:center;cursor:pointer;" id="data-items-table-csv" target="_blank">Download CSV</a>
    </div>

  </div>

  <div class="data-table table-responsive">
    <table class="table table-striped table-borderless">
      <thead>
        <tr>
          <th scope="col">
            DATE <span class="data-short">
              <a href="#" class="active">
                <i class="fe fe-chevron-up"></i>
              </a>
              <a href="#">
                <i class="fe fe-chevron-down"></i>
              </a>
            </span>
          </th>
          <th scope="col" class="twitter-col">
            TEXT <span class="data-short">
              <a href="#">
                <i class="fe fe-chevron-up"></i>
              </a>
              <a href="#">
                <i class="fe fe-chevron-down"></i>
              </a>
            </span>
          </th>
          <th scope="col"  >
            SOURCE <span class="data-short">
              <a href="#">
                <i class="fe fe-chevron-up"></i>
              </a>
              <a href="#">
                <i class="fe fe-chevron-down"></i>
              </a>
            </span>
          </th>
          <th scope="col" class="text-center">
            WEIGHTED <span class="data-short">
              <a href="#">
                <i class="fe fe-chevron-up"></i>
              </a>
              <a href="#">
                <i class="fe fe-chevron-down"></i>
              </a>
            </span>
          </th>
          <th scope="col" class="text-center" >
            RAW <span class="data-short">
              <a href="#">
                <i class="fe fe-chevron-up"></i>
              </a>
              <a href="#">
                <i class="fe fe-chevron-down"></i>
              </a>
            </span>
          </th>
          <th scope="col" class="text-center" >
            LANGUAGE <span class="data-short">
              <a href="#">
                <i class="fe fe-chevron-up"></i>
              </a>
              <a href="#">
                <i class="fe fe-chevron-down"></i>
              </a>
            </span>
          </th>
         
        </tr>
      </thead>
      <tbody id="data-table-content">
      </tbody>
    </table>
  </div>

  <div class="table-bottom" id="data-table-pagination">
  </div>
</div>
</div>
`
export function createTable(page){
    createHTML(html)
    let content = document.getElementById("data-table-content");

    update.startUpdate()
    content.innerHTML = "Loading...";
    let pagination = document.getElementById("data-table-pagination");
    pagination.innerHTML = ""
    let pageSize = document.getElementById("data-table-page-size").value
    let filtersValues = getFilters() 
    let urlParams = new URLSearchParams({
        "date-from": filtersValues.dateFrom,
        "date-to": filtersValues.dateTo,
        "languages": encodeURIComponent(filtersValues.languages),
        "sources": encodeURIComponent(filtersValues.sources)
    })
    document.getElementById("data-items-table-csv").href = `/api/new-data/project/${window.project_id}/?format=csv&` + urlParams
    fetch(`/api/new-data/project/${window.project_id}/?page=${page}&page-size=${pageSize}&` + urlParams)
    .then((response) => response.json())
    .then((data) => {
        content.innerHTML = "";
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
        createPagination(firstElement, lastElement, data.total, data.currentPage, data.totalPages, pagination, createTable);
        update.finishUpdate()
    });
}
//createTable(1);
/*
<div class="col-12 col-md-auto">
        <ul class="pagination">
        <li>
            <a href="#">
            <i class="fe fe-chevron-left"></i>
            </a>
        </li>
        <li class="active">
            <a href="#">01</a>
        </li>
        <li>
            <a href="#">02</a>
        </li>
        <li>
            <a href="#">03</a>
        </li>
        <li>
            <a href="#">04</a>
        </li>
        <li>
            <a href="#">..</a>
        </li>
        <li>
            <a href="#">25</a>
        </li>
        <li>
            <a href="#"> <i class="fe fe-chevron-right"></i></a>
        </li>
        
        </ul>
    </div>
*/