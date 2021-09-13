
function standard_map(data, smoothing){

    var arr = [];

    if (smoothing == "off") {
        arr.push(data["incidents"]);
        arr.push(data["bwratio"]);
        arr.push(data["slci"]);
        arr.push(data["perc_republican_votes"]);
        template = "Selection ratio: %{customdata[2]}<br>Incidents: %{customdata[0]}<br>Black/White population ratio: %{customdata[1]:.3f}<br>Republican vote share: %{customdata[3]}\%<extra></extra>"
    } else if(!("slci" in data)) {
        arr.push(data["incidents"]);
        arr.push(data["bwratio"]);
        arr.push(data["selection_ratio"]);
        arr.push(data["perc_republican_votes"]);
        template = "Selection ratio: %{customdata[2]}<br>Incidents: %{customdata[0]}<br>Black/White population ratio: %{customdata[1]:.3f}<br>Republican vote share: %{customdata[3]}\%<extra></extra>"
    }

    transpose = m => m[0].map((x,i) => m.map(x => x[i]))
    
    arr = transpose(arr);
    
    var data = [{
        type: "choroplethmapbox", z: data["selection_ratio_log10"], locations: data["FIPS"],
        geojson: 'https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json',
        zmin:-2,
        zmax:2,
        opacity: 0.6,
        colorscale: "Viridis",
        customdata: arr,
        hovertemplate: template,
      }];
      
      var layout = {"uirevision":"test", "margin": {"t": 0, "b": 0, "l": 0, r:"0"}, mapbox: {center: {'lat': 40.567243, 'lon': -96.271556}, zoom: 3.7, style:"carto-positron"}};
      
      var config = {mapboxAccessToken: "pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNrOWJqb2F4djBnMjEzbG50amg0dnJieG4ifQ.Zme1-Uzoi75IaFbieBDl3A"};
      
      return {data: data, layout: layout, config: config};
}

function getAllIndexes(arr, val) {
    var indexes = [], i;
    for(i = 0; i < arr.length; i++)
        if (arr[i] === val)
            indexes.push(i);
    return indexes;
}

function confidence_map(data){

    var Figure = {'data': [], 'layout': {"uirevision":"test", "margin": {"t": 0, "b": 0, "l": 0, r:"0"}, "showlegend": true, mapbox: {center: {'lat': 40.567243, 'lon': -96.271556}, zoom: 3.7, style:"carto-positron"}}, 'config': {mapboxAccessToken: "pk.eyJ1IjoiYnJhZGxleWJ1dGNoZXIiLCJhIjoiY2t0Y3I0ZHBjMjhkNzJ2bGFrNGR6cWFycSJ9.cREa4cbb8CChjWfTKMWQbQ"}};

    color_map = {
        "S>5":"#E76258",
        "S>2":"#EAB055",
        "S>1":"#E0D987",
        "S<1":"#5E925F",
        "S<0.5":"#265F47",
        "S<0.2":"#52675B",
        "Low confidence":"#689891"
    };
    

    for (const color of Object.keys(color_map)) {

        var fips = Array.from(data["FIPS"]);
        var cats = Array.from(data["cat"]);

        var idxs = getAllIndexes(cats, color);

        var z = new Array(idxs.length).fill(1);

        var fips = idxs.map(i => fips[i]);

        var arr = [];

        arr.push(idxs.map(i => data["incidents"][i]));
        arr.push(idxs.map(i => data["bwratio"][i]));
        arr.push(idxs.map(i => data["slci"][i]));
        arr.push(idxs.map(i => data["cat"][i]));
        arr.push(idxs.map(i => data["perc_republican_votes"][i]));

        transpose = m => m[0].map((x,i) => m.map(x => x[i]))
        
        arr = transpose(arr);

        var pldata = {
            type: "choroplethmapbox",
            z: z,
            locations: fips, 
            geojson: 'https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json',
            colorscale: [[0.0, color_map[color]], [1.0, color_map[color]]],
            name: color,
            customdata: arr,
            opacity: 0.6,
            showscale: false,
            showlegend: true,
            hovertemplate:
            "Category: %{customdata[3]}<br>Selection ratio: %{customdata[2]}<br>Incidents: %{customdata[0]}<br>Black/White population ratio: %{customdata[1]:.3f}<br>Republican vote share: %{customdata[4]}\%<extra></extra>"
        };

        Figure["data"].push(pldata)
    }
                  
    return Figure;
}

function quantile_map(data){

    var Figure = {'data': [], 'layout': {"uirevision":"test", "margin": {"t": 0, "b": 0, "l": 0, r:"0"}, "legend": {"title": {"text": "Selection Ratio Quantiles"}}, "showlegend": true, mapbox: {center: {'lat': 40.567243, 'lon': -96.271556}, zoom: 3.7, style:"carto-positron"}}, 'config': {mapboxAccessToken: "pk.eyJ1IjoiYnJhZGxleWJ1dGNoZXIiLCJhIjoiY2t0Y3I0ZHBjMjhkNzJ2bGFrNGR6cWFycSJ9.cREa4cbb8CChjWfTKMWQbQ"}};

    color_map = {
        "75":"#E76258",
        "50":"#E0D987",
        "25":"#616161",
        "0":"#689891"
    };
    

    for (const color of Object.keys(color_map)) {

        var fips = Array.from(data["FIPS"]);
        var cats = Array.from(data["quantiles"]).map(String);

        var idxs = getAllIndexes(cats, color);

        var z = new Array(idxs.length).fill(1);

        var fips = idxs.map(i => fips[i]);

        var arr = [];

        arr.push(idxs.map(i => data["incidents"][i]));
        arr.push(idxs.map(i => data["bwratio"][i]));
        arr.push(idxs.map(i => data["slci"][i]));
        arr.push(idxs.map(i => data["percentiles"][i]));
        arr.push(idxs.map(i => data["perc_republican_votes"][i]));

        transpose = m => m[0].map((x,i) => m.map(x => x[i]))
        
        arr = transpose(arr);

        var pldata = {
            type: "choroplethmapbox",
            z: z,
            locations: fips, 
            geojson: 'https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json',
            colorscale: [[0.0, color_map[color]], [1.0, color_map[color]]],
            name: color,
            customdata: arr,
            opacity: 0.6,
            showscale: false,
            showlegend: true,
            hovertemplate:
            "Percentile: %{customdata[3]}<br>Selection Ratio: %{customdata[2]}<br>Incidents: %{customdata[0]}<br>Black/White population ratio: %{customdata[1]:.3f}<br>Republican vote share: %{customdata[4]}\%<extra></extra>"
        };

        Figure["data"].push(pldata)
    }
                  
    return Figure;
}

window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        get_map: function(data, maptype, smoothing) {
            if (maptype == "standard") {
                return standard_map(data, smoothing);
            } else if (maptype == "confidence") {
                return confidence_map(data);
            } else {
                return quantile_map(data);
            }
        }
    }
});