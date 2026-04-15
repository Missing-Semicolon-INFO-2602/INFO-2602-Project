const mount = document.getElementById("tree");

if (mount) {
  fetch("/api/animals/tree", { credentials: "same-origin" })
    .then(r => r.json())
    .then(data => renderRadialTree(data))
    .catch(err => { mount.textContent = `Tree failed to load: ${err.message}`; });
}

function renderRadialTree(data) {
  const width = 820;
  const cx = width * 0.5;
  const cy = width * 0.5;
  const radius = Math.min(width, width) / 2 - 80;

  const tree = d3.tree()
    .size([2 * Math.PI, radius])
    .separation((a, b) => (a.parent === b.parent ? 1 : 2) / a.depth);

  const root = tree(d3.hierarchy(data));

  const svg = d3.create("svg")
    .attr("viewBox", [-cx, -cy, width, width])
    .attr("style", "font: 10px sans-serif;");

  svg.append("g")
    .attr("fill", "none")
    .attr("stroke", "#56be5b")
    .attr("stroke-opacity", 0.5)
    .attr("stroke-width", 1.2)
    .selectAll("path")
    .data(root.links())
    .join("path")
    .attr("d", d3.linkRadial()
      .angle(d => d.x)
      .radius(d => d.y));

  svg.append("g")
    .selectAll("circle")
    .data(root.descendants())
    .join("circle")
    .attr("transform", d => `rotate(${d.x * 180 / Math.PI - 90}) translate(${d.y},0)`)
    .attr("fill", d => d.children ? "#38f882" : "#f8fafc")
    .attr("r", 2.5);

  svg.append("g")
    .attr("stroke-linejoin", "round")
    .attr("stroke-width", 3)
    .selectAll("text")
    .data(root.descendants().filter(d => !d.children))
    .join("text")
    .attr("transform", d => `rotate(${d.x * 180 / Math.PI - 90}) translate(${d.y},0) rotate(${d.x >= Math.PI ? 180 : 0})`)
    .attr("dy", "0.31em")
    .attr("x", d => d.x < Math.PI === !d.children ? 6 : -6)
    .attr("text-anchor", d => d.x < Math.PI === !d.children ? "start" : "end")
    .attr("paint-order", "stroke")
    .attr("stroke", "#113b1a")
    .attr("fill", "#f8fafc")
    .text(d => d.data.name);

  mount.appendChild(svg.node());
}
