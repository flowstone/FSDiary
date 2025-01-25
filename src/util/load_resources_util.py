

class LoadResourcesUtil:
    # 静态资源定义
    @staticmethod
    def static_resources():
        static_resources = """
        <html>
        <head>
            <link href="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/themes/prism-coy.min.css" rel="stylesheet">
            <script src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/prism.min.js" async></script>
            <script src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/plugins/autoloader/prism-autoloader.min.js" async></script>
            <script src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/components/prism-python.min.js" async></script>
            <script src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/components/prism-java.min.js" async></script>
            <script src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/components/prism-php.min.js" async></script>
            <script src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/components/prism-bash.min.js" async></script>
            <script src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/components/prism-javascript.min.js" async></script>
            <script src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/components/prism-docker.min.js" async></script>
            <script src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/components/prism-json.min.js" async></script>
            <script src="https://cdn.jsdelivr.net/npm/prismjs@1.29.0/components/prism-css.min.js" async></script>
        </head>
        <body></body>
        </html>
        """
        return static_resources
