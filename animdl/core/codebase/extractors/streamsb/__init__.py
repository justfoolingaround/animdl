import binascii

import regex
import yarl

PAYLOAD = "616e696d646c616e696d646c7c7c{}7c7c616e696d646c616e696d646c7c7c73747265616d7362/616e696d646c616e696d646c7c7c363136653639366436343663363136653639366436343663376337633631366536393664363436633631366536393664363436633763376336313665363936643634366336313665363936643634366337633763373337343732363536313664373336327c7c616e696d646c616e696d646c7c7c73747265616d7362"
CONTENT_ID_REGEX = regex.compile(r"/e/([^?#&/.]+)")


def extract(session, url, **opts):

    content_id = CONTENT_ID_REGEX.search(url).group(1)
    content_url = "https://{}/".format(yarl.URL(url).host)

    sources = (
        session.get(
            content_url
            + "sources41/{}".format(
                PAYLOAD.format(binascii.hexlify(content_id.encode()).decode())
            ),
            headers={"watchsb": "streamsb"},
        )
        .json()
        .get("stream_data", {})
    )

    return [
        {"stream_url": sources.get("file"), "headers": {"referer": content_url}},
        {"stream_url": sources.get("backup"), "headers": {"referer": content_url}},
    ]
