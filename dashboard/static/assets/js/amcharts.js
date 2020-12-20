//<!-- Styles -->
{
  /* <style>
  #chartdiv {
    width: 100%;
    height: 600px;
  }
</style> */
}

//<!-- Resources -->

//<!-- Chart code -->

am4core.ready(function () {
  // Themes begin
  am4core.useTheme(am4themes_dataviz);
  am4core.useTheme(am4themes_animated);
  // Themes end

  var chart = am4core.create("chartdiv", am4plugins_wordCloud.WordCloud);
  chart.fontFamily = "sans-serif";
  var series = chart.series.push(new am4plugins_wordCloud.WordCloudSeries());
  series.randomness = 0.1;
  series.rotationThreshold = 0.5;
  var data = [];
  for (var i = 0; i < project_data?.keywords?.length; i++) {
    data.push({
      tag: project_data.keywords[i][0],
      count: project_data.keywords[i][1],
    });
  }
  series.data = data;

  series.dataFields.word = "tag";
  series.dataFields.value = "count";

  series.heatRules.push({
    target: series.labels.template,
    property: "fill",
    min: am4core.color("#dd9942"),
    max: am4core.color("#537fd6"),
    dataField: "value",
  });


  // series.labels.template.url = "#{word}";
  // series.labels.template.urlTarget = "_blank";
  series.labels.template.tooltipText = "{word}: {value}";

  var hoverState = series.labels.template.states.create("hover");
  hoverState.properties.fill = am4core.color("#FF0000");

}); // end am4core.ready()
