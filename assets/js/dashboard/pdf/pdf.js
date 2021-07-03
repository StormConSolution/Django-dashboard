import {jsPDF} from 'jspdf'
let graphs = {}
export function storeGraph(key, data){
    graphs[key] = data
}

export function getGraphs(){
    return graphs
}

export function generatePDF(){
    let doc = new jsPDF()
    doc.text("Repustate Report", 10, 10)
    //doc.addImage(graphs["overall-sentiment"], 'PNG', 10, 100);
    doc.addImage(graphs["overall-sentiment"], 'PNG', 10, 300);
    doc.save("report.pdf")
}

export function saveGraph(chart, key, width){
    setTimeout(()=>{
        chart.dataURI({width:width}).then(({imgURI, blob})=>{
            storeGraph(key, imgURI)
    })},3000)
}