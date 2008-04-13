## -*- coding: utf-8 -*-
<%include file="header.mako"/>

    <div class="main">

        <div class="left">

            <div class="content">

                <h1><a href=" ${p.url} ">${p.title}</a></h1>
                <div class="descr">
                    Article numéro ${p.realid} écrit ${p.get_time} dans les catégories :
                    % for t in p.tags:
                            <a href=" ${t.url} "> ${t.tagname} </a>
                    % endfor
                </div>
                ${p.html_content}
            </div>

        </div>

        <div class="right">

            <div class="subnav">

                <h1>Kib's Memo</h1>
                <p>Un blog sur Python, LaTeX et la programmation en général.</p>

                <h1>Les 10 Derniers billets</h1>
                <ul>
                % for k in articles[:10]:
                    <li><a href=" ${k.url} "> ${k.title} </a></li>
                % endfor
                </ul>

                <h1>Catégories</h1>
                <ul>
                    % for t in tags:
                        <li><a href=" ${t.url} "> ${t.tagname} (${t.get_number_of_posts})</a></li>
                    % endfor
                </ul>

                <%include file="links_right.mako"/>

            </div> <!-- subnav -->

        </div> <!-- right -->

        <div class="clearer"><span></span></div>

    </div>

    <div class="footer">
            <%include file="footer.mako"/>
    </div>

</div>

</body>
</html>
