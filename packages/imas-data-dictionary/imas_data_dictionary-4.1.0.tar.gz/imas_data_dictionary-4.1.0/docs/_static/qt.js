let searchString = "";
let data_type = "";
let coords = "";

searchString = document.getElementById("search_input").value = "";
data_type = document.getElementById("data_type_input").value = "";
coords = document.getElementById("coords_input").value = "";

let ignore_keywords = ["the", "to", "of", "for", "by", "and", "on", "or",
    "with", "that", "has", "will", "this", "as", "a", "an", "then", "in", "when",
    "be", "been", , "encountered", "meaning", "shall", "not", "can", "each", "various", "given", "are", "used", "is", "put", "in",
    "at", "either", "taken", "from", "over", "such", "into", "takes", "some"];

const occurring_data_types = new Set();
const data_types_result = xmlDoc.evaluate('//field/@data_type', xmlDoc, null, XPathResult.ANY_TYPE, null);

let node = null;
while ((node = data_types_result.iterateNext())) {
    occurring_data_types.add(node.textContent);
}

//console.log(occurring_data_types);


occurring_data_types.forEach(type => {

    let option = document.createElement("option");
    option.setAttribute("value", type);
    document.getElementById("occuring_data_types").appendChild(option);

})


function onSearchChanged(e) {
    onFiltersChanged();
}

function onDataTypeChanged(e) {
    onFiltersChanged();
}

function onCoordsChanged(e) {
    onFiltersChanged();
}

let onFiltersChangedTimer;

function onFiltersChanged() {

    clearTimeout(onFiltersChangedTimer);

    onFiltersChangedTimer = setTimeout(() => {


        searchString = document.getElementById("search_input").value;
        data_type = document.getElementById("data_type_input").value;
        coords = document.getElementById("coords_input").value.split(" ").filter(coord => coord.length).map(coord => {
            if (coord.includes(':')) return { axis: coord.split(':')[0], value: coord.split(':')[1] };
            else return { value: coord };
        });

        //console.log("onFiltersChanged", searchString, data_type, coords);

        let keywords = searchString.match(/\b(\w+)'?(\w+)?\b/g)?.sort((a, b) => b.length - a.length).map(k => k.toLocaleLowerCase()) || [];

        if (keywords.length || data_type || coords.length) {

            const count_path_matches = "(" + keywords.map(
                keyword => "number(boolean(ancestor-or-self::*[starts-with(@name, '" + keyword + "')" + (keyword.length >= 2 ? " or contains(@name, '_" + keyword + "')" : "") + "]))"
            ).join(" + ") + ")";

            //const path_predicate = keywords.length ? count_path_matches + " >= " + keywords.length : "";

            const count_desc_matches = "(" + keywords.map(keyword =>
                "number(not(ancestor-or-self::*[starts-with(@name, '" + keyword + "')" + (keyword.length >= 2 ? " or contains(@name, '_" + keyword + "')" : "") + "]) and contains(concat(' ', translate(@documentation, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')), ' " + keyword + "'))"
            ).join(" + ") + ")";

            //const desc_predicate = keywords.length ? "((" + count_desc_matches + " div (" + keywords.length + " - " + count_path_matches + ")) >= 0.8)" : "";

            const keywords_predicate = keywords.length ? "((" + count_path_matches + " + " + count_desc_matches + ") >= " + keywords.length + ")" : "";

            const data_type_predicate = data_type ? "contains(@data_type, '" + data_type + "')" : "";

            //TODO: Stopped here, not done at all, replacing maxoccur by coords...
            const coords_predicate = coords.length ? "(" + coords.map(coord => {
                return `(@*[starts-with(name(), 'coordinate${coord.axis || ''}') and (('${coord.value}' = substring(., string-length(.) - string-length('${coord.value}') + 1)) or (string-length(substring-after(., '${coord.value}')) and not(contains(substring-after(., '${coord.value}'), '/'))))])`
            }).join(' and ') + ")" : "";

            const predicates = [];
            if (data_type_predicate) predicates.push(data_type_predicate);
            if (coords_predicate) predicates.push(coords_predicate);
            if (keywords_predicate) predicates.push(keywords_predicate);

            const selectStatement = `//*${predicates.length ? "[" + predicates.join(' and ') + "]" : ""}`;

            //console.log(selectStatement)

            const sortStatement = keywords.length ? `(${count_path_matches} * 100) - (count(ancestor-or-self::*[@name]) + (string-length(concat(@name, ancestor::node()[1]/@name, ancestor::node()[2]/@name, ancestor::node()[3]/@name, ancestor::node()[4]/@name)) * 0.2)) + number(boolean(ancestor-or-self::IDS[${keywords.map(
                keyword => "starts-with(@name, '" + keyword + "')"
            ).join(" or ")}])) + (number(${keywords.map(
                keyword => "not(ancestor-or-self::*[starts-with(@name, '" + keyword + "')" + (keyword.length >= 2 ? " or contains(@name, '_" + keyword + "')" : "") + "]) and starts-with(translate(@documentation, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '" + keyword + "')"
            ).join(" or ")}) * 20)` : "1";

            //console.log(sortStatement)


            let resultDocument = searchXMLDoc(selectStatement, sortStatement);
            const search_results_element = document.getElementById("search_results");
            search_results_element.innerHTML = "";

            if (resultDocument.hasChildNodes())
                search_results_element.appendChild(resultDocument);
            else search_results_element.innerHTML = '<div id="no_results_message">No results</div>';

            if (keywords.length) {
                const pattern = new RegExp(`([^<>]*?)(${keywords.join('|')})(?![^<>]*?>)`, 'gi');
                // Replace each occurrence of a keyword with the encapsulated version
                search_results_element.querySelectorAll(".path a, .description").forEach(u =>
                    u.innerHTML = u.innerHTML.replaceAll(pattern, function (match, p1, p2) {
                        return p1 + '<span class="highlight">' + p2 + '</span>';
                    })
                )
            }

            if (coords.length) {
                search_results_element.querySelectorAll(".coord .axis").forEach(u => {
                    let coord = coords.find(coord => coord.axis == u.innerHTML);
                    if (coord)
                        u.innerHTML = '<span class="highlight">' + coord.axis + '</span>';
                })

                const pattern = new RegExp(`([^<>]*?)(${coords.map(coord => coord.value).join('|')})(?![^<>]*?>)`, 'gi');
                // Replace each occurrence of a keyword with the encapsulated version

                search_results_element.querySelectorAll(".coord .value").forEach(u =>
                    u.innerHTML = u.innerHTML.replace(pattern, function (match, p1, p2) {
                        return p1 + '<span class="highlight">' + p2 + '</span>';
                    })
                )
            }

            document.getElementById("search_results_dropdown").style.display = "block";
            document.getElementById("search_results_dropdown").scrollTop = 0;

        } else {
            document.getElementById("search_results_dropdown").style.display = "none";
        }


    }, 500);
}


function searchXMLDoc(selectStatement, sortStatement) {

    const xsltString = `<?xml version="1.0"?>
    <xsl:stylesheet version="1.0" 
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
    xmlns:fn="http://www.w3.org/2005/02/xpath-functions">

        <xsl:output method="html"/>

        <xsl:template match="/*">
            <xsl:for-each select="${selectStatement}">

                <xsl:sort select="${sortStatement}" order="descending" data-type="number"/>

                <div class="item">

                    <xsl:variable name="page">
                        <xsl:value-of select="ancestor-or-self::IDS/@name" />
                    </xsl:variable>

                    <div class="head" >
                        <xsl:attribute name="onclick">onResultHeadClicked(event, '#<xsl:value-of select="$page"/><xsl:if test="@path">-<xsl:value-of select="translate(@path, '/', '-')"/></xsl:if>')</xsl:attribute>

                        <span class="path">
                            <xsl:for-each select="ancestor::*[@name]">
                                <a>
                                    <xsl:attribute name="href">../generated/ids/<xsl:value-of select="$page"/>.html#<xsl:value-of select="$page"/><xsl:if test="@path">-<xsl:value-of select="translate(@path, '/', '-')"/></xsl:if></xsl:attribute>
                                    <xsl:value-of select="@name"/>
                                </a>
                                <span>/</span>
                            </xsl:for-each>
                            <a>
                            <xsl:attribute name="href">../generated/ids/<xsl:value-of select="$page"/>.html#<xsl:value-of select="$page"/><xsl:if test="@path">-<xsl:value-of select="translate(@path, '/', '-')"/></xsl:if></xsl:attribute>
                                <xsl:value-of select="@name"/>
                            </a>
                        </span>
                    </div>

                    <div class="details">
                        <div class="flex">
                        
                            <span class="data_type">
                                <xsl:choose>
                                    <xsl:when test="name() = 'field'">
                                        <xsl:value-of select="@data_type"/>
                                    </xsl:when>
                                    <xsl:otherwise>
                                        <xsl:text>IDS</xsl:text>
                                    </xsl:otherwise>
                                </xsl:choose>
                            </span>

                            <xsl:if test="name() = 'field'">
                                <span class="coords">
                                        <div class="coords_dropdown">
                                                <xsl:for-each select="@*[starts-with(name(), 'coordinate')]">
                                                        <xsl:variable name="coord_index">
                                                                <xsl:value-of select="translate(name(), 'coordinatesm_', '')"/>
                                                        </xsl:variable>
                                                        <div>
                                                                <xsl:choose>
                                                                        <xsl:when test="contains(name(), 'same_as')">
                                                                                <xsl:attribute name='class'>coord same_as</xsl:attribute>
                                                                        </xsl:when>
                                                                        <xsl:when test="ancestor::*[@*[name() = concat('coordinate', $coord_index, '_same_as')]]">
                                                                                <xsl:attribute name='class'>coord has_same_as</xsl:attribute>
                                                                        </xsl:when>
                                                                        <xsl:otherwise>
                                                                                <xsl:attribute name='class'>coord</xsl:attribute>
                                                                        </xsl:otherwise>
                                                                </xsl:choose>
                                                                <span class="axis"><xsl:value-of select="$coord_index"/></span>
                                                                :
                                                                <span class="value"><xsl:value-of select="."/></span>
                                                        </div>
                                                </xsl:for-each>
                                        </div>
                                </span>
                            </xsl:if>
                        
                        </div>

                        <div class="description">
                            <xsl:value-of select="@documentation"/>
                        </div>
                    </div>

                </div>

            </xsl:for-each>
        </xsl:template>

    </xsl:stylesheet>
    `;

    const xsltProcessor = new XSLTProcessor();
    const xsltDoc = parser.parseFromString(xsltString, "application/xml");
    xsltProcessor.importStylesheet(xsltDoc);

    return xsltProcessor.transformToFragment(xmlDoc, document);

}

window.addEventListener('click', function (e) {
    if (Array.from(document.querySelectorAll('#search_results_dropdown, .search_field')).find(elem => elem.contains(e.target))) {
    } else {
        document.getElementById("search_results_dropdown").style.display = "none";
    }
});


function toggleField(id) {
    //console.log("toggleField", id)
    document.getElementById(id).classList.toggle('expanded');
}

function toggleAdvancedSearch() {
    if (!document.getElementById("search_fields").classList.toggle('advanced')) {
        document.getElementById("data_type_input").value = "";
        document.getElementById("coords_input").value = "";
    }
}

function onResultHeadClicked(event, hash) {
    event.stopPropagation();
    //console.log(event.target, event.target.nodeName)

    if (event.target.classList.contains("path") || event.target.classList.contains("head"))
        window.location = hash;

}

document.body.classList.add('ready');