import React from 'react';

const DataTableModalRows = (props) => {
    let dataItems = []
    for (let element of props.data) {
        const length = 150;
        let text = "";
        if(element.text.length > length){
            text = element.text.substring(0, length) + "...";
        } else {
            text = element.text
        }
        dataItems.push(
            <tr key={element.id}>
                <td>
                    <input className="ml-auto form-check-input" type="checkbox" data-role="checkbox-bulk-action"
                           data-item-id={element.id}/>
                </td>
                <td>
                    <small>{element.dateCreated}</small>
                </td>
                <td>
                    {text}
                </td>
                <td>
                    <b><a href={element.url}>{element.sourceLabel}</a></b>
                </td>
                <td className="text-center">
                    {element.sentimentValue.toFixed(4)}
                </td>
                <td className="text-center">
                    <a href="#" className="info-button">{element.languageCode}</a>
                </td>
                <td className="text-center">
                    <a className="mr-1 ml-0" style={{cursor: "pointer"}} data-toggle="tooltip"
                       data-role="edit-data-item"
                       data-placement="bottom" title="Edit" onClick={editDataItem} data-item-id={element.id}>
                        <i className="fe fe-edit"></i>
                    </a>
                    <a className="mr-1 ml-1" style={{cursor: "pointer"}} data-toggle="tooltip"
                       data-role="refresh-data-item"
                       data-placement="bottom" data-item-id={element.id} onClick={refreshDataItem} title="Re-analyze">
                        <i className="fe fe-refresh-cw"></i>
                    </a>
                    <a className="mr-0 ml-1" style={{cursor: "pointer"}} data-toggle="tooltip"
                       data-role="delete-data-item"
                       data-placement="bottom" data-item-id={element.id} onClick={deleteDataItem} title="Delete">
                        <i className="fe fe-trash-2"></i>
                    </a>
                </td>
            </tr>)
        }
    return (
        <>
            {dataItems}
        </>
    );
}

export default DataTableModalRows

let editDataItem = element => {
    let target = element.currentTarget
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
}

let refreshDataItem = element=> {
    let target = element.currentTarget
    let dataID = target.getAttribute("data-item-id")
    console.log(dataID)
    fetch(`/api/data-item/${dataID}/`, {
        method:"PUT",
        credentials:"include"
    })
        .then(response =>{
            console.log("test")
            if(response.status == 200){
                location.reload()
            }
        })
}

let deleteDataItem = element => {
    let target = element.currentTarget
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
}