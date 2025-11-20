def get_tooltip_css(dark_mode):
    return '''
    <style>
        .tooltip-word {
            color: #0066cc;
            cursor: help;
            text-decoration: underline dotted;
            position: relative;
            display: inline-block;
        }
        
        .tooltip-content {
            position: absolute;
            bottom: 100%;
            left: 50%;
            transform: translateX(-50%);
            background: white;
            border: 1px solid #ccc;
            border-radius: 8px;
            padding: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            min-width: 250px;
            z-index: 1000;
            margin-bottom: 8px;
            display: none;
        }
        
        .tooltip-content.active {
            display: block;
        }
        
        .tooltip-content::after {
            content: "";
            position: absolute;
            top: 100%;
            left: 50%;
            margin-left: -5px;
            border-width: 5px;
            border-style: solid;
            border-color: white transparent transparent transparent;
        }
        
        .tooltip-description {
            margin-bottom: 10px;
            color: #333;
            font-size: 14px;
        }
        
        .tooltip-links {
            display: flex;
            flex-direction: column;
            gap: 5px;
        }
        
        .tooltip-link {
            color: #0066cc;
            text-decoration: none;
            font-size: 13px;
            padding: 4px 8px;
            border-radius: 4px;
            transition: background-color 0.2s;
        }
        
        .tooltip-link:hover {
            background-color: #f0f0f0;
        }
        
        .loading {
            color: #666;
            font-style: italic;
        }
    </style>
    '''