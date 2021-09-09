
function standard_map(data){

    var arr = [];

    arr.push(data["incidents"]);
    arr.push(data["bwratio"]);
    arr.push(data["slci"]);


    transpose = m => m[0].map((x,i) => m.map(x => x[i]))
    arr = transpose(arr);
    
    console.log(arr[0]);

    var data = [{
        type: "choroplethmapbox", z: data["selection_ratio_log10"], locations: data["FIPS"],
        geojson: 'https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json',
        zmin:-2,
        zmax:2,
        colorscale: "Viridis",
        customdata: arr,
        hovertemplate:
            "Selection Ratio: %{customdata[2]}<br>Incidents: %{customdata[0]}<br>Black-White Population Ratio: %{customdata[1]:.3f}<extra></extra>"
      }];
      
      var layout = {mapbox: {center: {'lat': 41.567243, 'lon': -101.271556}, zoom: 3.7, style:"carto-positron"}};
      
      var config = {mapboxAccessToken: "pk.eyJ1IjoiYnJhZGxleWJ1dGNoZXIiLCJhIjoiY2t0Y3I0ZHBjMjhkNzJ2bGFrNGR6cWFycSJ9.cREa4cbb8CChjWfTKMWQbQ"};
      
      return {data: data, layout: layout, config: config};
}

function confidence_map(data){
    var data = [{
        type: "choroplethmapbox", z: data["cat"], locations: data["FIPS"],
        geojson: 'https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json'
      }];
      
      var layout = {mapbox: {center: {'lat': 41.567243, 'lon': -101.271556}, zoom: 3.7, style:"carto-positron"}};
      
      var config = {mapboxAccessToken: "pk.eyJ1IjoiYnJhZGxleWJ1dGNoZXIiLCJhIjoiY2t0Y3I0ZHBjMjhkNzJ2bGFrNGR6cWFycSJ9.cREa4cbb8CChjWfTKMWQbQ"};
      
      return {data: data, layout: layout, config: config};
}

window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        get_map: function(data, maptype) {
            if (maptype == "standard") {
                return standard_map(data);
            } else {
                return confidence_map(data);
            }
        }
    }
});