import difflib
from ._cfg import G_SERVERS


class ServerLoader:
    
    @staticmethod
    def get(label: str):
        """
        Return (url, header) for your server.
        Example:
            url, header = ServerLoader.get("Romania 1")
        """
        # exact match (case-insensitive)
        for name, (url, header) in G_SERVERS.items():
            if name.lower() == label.lower():
                return url, header

        # fallback fuzzy 
        all_labels = list(G_SERVERS.keys())
        best = difflib.get_close_matches(label, all_labels, n=1, cutoff=0.5)
        if best:
            return G_SERVERS[best[0]]

        #nothing to find
        raise ValueError(f"Server '{label}' not present in server list.")