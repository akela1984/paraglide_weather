function deg2rad(deg) {
  return deg * (Math.PI / 180.0);
}

function drawWindCompass(canvas, yellows, greens) {
  if (yellows == null || greens == null) return;

  let padding = 7;
  let borderLineWidth = 3;
  let textSize = 21;
  let textStrokeSize = 1;
  const compassPoints = ["S", "E", "N", "W"];
  let r = Math.min(canvas.width, canvas.height) / 2 - textSize / 2;

  let ctx = canvas.getContext("2d");
  let center = [canvas.width / 2, canvas.height / 2];
  // Yellows
  ctx.fillStyle = "#e6e619";
  yellows.forEach(function (zone) {
    ctx.beginPath();
    ctx.moveTo(center[0], center[1]);
    ctx.arc(
      center[0],
      center[1],
      r,
      deg2rad(zone[0] - 90),
      deg2rad(zone[1] - 90)
    );
    ctx.closePath();
    ctx.fill();
  });

  // Greens
  ctx.fillStyle = "#30cc1f";
  greens.forEach(function (zone) {
    ctx.beginPath();
    ctx.moveTo(center[0], center[1]);
    ctx.arc(
      center[0],
      center[1],
      r,
      deg2rad(zone[0] - 90),
      deg2rad(zone[1] - 90)
    );
    ctx.closePath();
    ctx.fill();
  });

  // Outer Rim
  ctx.strokeStyle = "#000";
  ctx.lineWidth = borderLineWidth;
  ctx.beginPath();
  ctx.arc(center[0], center[1], r, 0, Math.PI * 2);
  ctx.closePath();
  ctx.stroke();

  // Points of the Compass
  ctx.strokeStyle = "#000";
  ctx.fillStyle = "#3ff";
  ctx.font = "bold " + textSize + "px Arial";
  ctx.lineWidth = textStrokeSize;
  compassPoints.forEach(function (pt, idx) {
    const th = deg2rad(idx * 90);
    const x = center[0] + Math.sin(th) * r;
    const y = center[1] + Math.cos(th) * r;

    ctx.fillText(pt, x - textSize / 3, y + textSize / 3);
    ctx.strokeText(pt, x - textSize / 3, y + textSize / 3);
  });
}

const markerColors = ["blue", "green", "gold", "violet", "grey", "orange"];
let icons = [];
markerColors.forEach(function (color) {
  icons.push(
    new L.Icon({
      iconUrl: `https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-${color}.png`,
      shadowUrl:
        "https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png",
      iconSize: [25, 41],
      iconAnchor: [12, 41],
      popupAnchor: [1, -34],
      shadowSize: [41, 41],
    })
  );
});

let redMarker = new L.Icon({
  iconUrl: `https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png`,
  shadowUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

$(function () {
  let maps = [];

  $(".accordion-collapse").on("shown.bs.collapse", function () {
    let mapDOM = $(this).find(".placeMap").first();
    let mapId = mapDOM.attr("id");
    if (maps.hasOwnProperty(mapId)) return;
    let map = L.map(mapId).setView(
      [mapDOM.data("lat"), mapDOM.data("lon")],
      13
    );
    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
      attribution:
        '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    }).addTo(map);

    let markers = [];
    markers.push(
      L.marker([mapDOM.data("lat"), mapDOM.data("lon")], {
        icon: redMarker,
      }).addTo(map)
    );

    mapDOM.data("subplaces").forEach(function (subplace, idx) {
      markers.push(
        L.marker([subplace.lat, subplace.lon], {
          icon: icons[idx],
          title: subplace.name,
        }).addTo(map)
      );
    });

    let group = new L.featureGroup(markers);
    map.fitBounds(group.getBounds().pad(0.5));
  });

  $(".compass-canvas").each(function () {
    drawWindCompass(
      $(this)[0],
      $(this).data("yellows"),
      $(this).data("greens")
    );
  });

  
});
