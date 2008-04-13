## -*- coding: utf-8 -*-
<%include file="header.mako"/>

    <div class="main">

        <div class="left">

            <div class="content">

                % for post in articles[:10]:
                <h1><a class="post" href=" ${post.url} ">${post.title}</a></h1>
                <div class="descr">
                    Article ${post.realid} écrit ${post.get_time} dans les catégories :
                    % for t in post.tags:
                            <a href=" ${t.url} "> ${t.tagname} </a>
                    % endfor
                </div>
                ${post.html_content}
                % endfor
            </div>

        </div>

        <div class="right">

            <div class="subnav">

                <h1>Kib's Memo</h1>
                <p>Un blog sur Python, LaTeX et la programmation en général.</p>
                <p><a href="http://kib2.free.fr/Articles/flux.xml" title="Kib's memo feed"><img src="http://kib2.free.fr/Articles/feed-icon32x32.png" alt="Feed icon" border="0" /></a>Flux RSS Kib's articles</p>

                <h1><img style="vertical-align:middle;" src="http://kib2.free.fr/Articles/billet.png" alt="Billet icon" border="0" />Les 10 Derniers billets</h1>
                <ul>
                % for p in articles[:10]:
                    <li><a href=" ${p.url} "> ${p.title} </a></li>
                % endfor
                </ul>

                <h1><img style="vertical-align:middle;" src="http://kib2.free.fr/Articles/categorie.png" alt="categorie icon" border="0" />Catégories</h1>
                <ul>
                    
                    % for t in tags:
                        <li><a href=" ${t.url} "> ${t.tagname} (${t.get_number_of_posts})</a></li>
                    % endfor
                </ul>
                
                <h1><img style="vertical-align:middle;" src="http://kib2.free.fr/Articles/archives.png" alt="categorie icon" border="0" />Archives</h1>
                    % for annee in archive.keys():
                            <% 
                            import itertools
                            truc = itertools.groupby(archive[annee], lambda p:p.postdate.month)
                            %>
                            <ul>
                                % for k,g in truc :
                                    <li><a href="${k}_${annee}.html">${noms_mois[int(k)].decode('utf-8')} ${annee} (${len(list(g))})</a></li>
                                % endfor
                            </ul>
                    % endfor


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
