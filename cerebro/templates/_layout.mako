<!doctype html>
<html>
    <head>
        <title>Extramental</title>
        <link rel="stylesheet" href="http://fonts.googleapis.com/css?family=Open+Sans:300,400,600,800,800italic,700italic,700,300italic,400italic,600italic">
        % for url in webassets(request, \
                               "js/bower_components/codemirror/lib/codemirror.css", \
                               "css/*.less", \
                               output="style.css", \
                               filters="less"):
        <link rel="stylesheet" href="${url}">
        % endfor
    </head>
    <body>
        <section>
            <h1>Recipe Book</h1>
            <p>Here are some recipes.</p>
            <section>
                <h1>Breads</h1>
                <section>
                    <h1>French Baguette</h1>
                    <ul>
                        <li>Flour</li>
                    </ul>
                </section>
            </section>
        </section>
        % for url in webassets(request, \
                               "js/bower_components/codemirror/lib/codemirror.js", \
                               "js/bower_components/lodash/lodash.js", \
                               "js/bower_components/ot/dist/ot-min.js", \
                               "js/bower_components/sockjs-client/sockjs.js", \
                               "js/*.js"):
        <script src="${url}"></script>
        % endfor
    </body>
</html>