import {getFilters} from './helpers/filters'
export default function populateWordCloudModalContainer(url){
    let filters = getFilters()
    fetch(url + "?" + filters).then(response => response.json()).then( data => {
    })
}