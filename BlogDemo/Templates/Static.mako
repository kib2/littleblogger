<%include file="header.mako"/>

    <div class="main">

        <div class="left">

            <div class="content">

                <h1><a class="post"">${title}</a></h1>
                ${static}

            </div>

        </div>

        <div class="right">

            <div class="subnav">

                <h1>Kib's Memo</h1>
                <p>Un blog sur Python, LaTeX et la programmation en général.</p>

                <h1>Catégories</h1>
                <ul>
                    % for t in tags:
                        <li><a href=" ${t.url} "> ${t.tagname} (${t.get_number_of_posts})</a></li>
                    % endfor
                </ul>

                <%include file="links_right.mako"/>

            </div>

        </div>

        <div class="clearer"><span></span></div>

    </div>

    <div class="footer">
    <%include file="footer.mako"/>
    </div>

</div>

</body>

</html>
