class ParseRequest:
    @staticmethod
    def parse_one_param(all_params: str, find_param: str) -> str:
        position_label = all_params.find(find_param)
        not_full_label = all_params[position_label + len(find_param) + 1:]
        end_position_label = not_full_label.find("&")
        find_str = not_full_label
        if end_position_label != -1:
            find_str = not_full_label[:end_position_label]
        return find_str

    @staticmethod
    def parse_request(body: str, *args: str) -> dict:
        params = dict()
        for param in args:
            params[param] = ParseRequest.parse_one_param(body, param)
        return params
