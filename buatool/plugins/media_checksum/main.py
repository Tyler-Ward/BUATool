import subprocess


class MediaChecksum:
    """
      BUA tool plugin to compare the contents of media files

      This plugin will create a checkum of a media files contents to alloww matching of media files with altered metadata
    """

    name = "media_checksum"

    @staticmethod
    def generateFileData(filename):
        process = subprocess.Popen(
            [
                "ffmpeg",
                "-i",
                filename,
                "-map", "0:a",
                "-codec", "copy",
                "-hide_banner",
                "-loglevel", "warning",
                "-f", "md5",
                "-"
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        output_split = stdout.decode("utf8").strip().split('=')

        if len(output_split) == 2:
            return output_split[1]
        else:
            return None
 
    @staticmethod
    def findMatches(filename, index):

        matches=[]

        media_csum = MediaChecksum.generateFileData(filename)

        hashmatches = index.findValue("media_checksum", media_csum)
        for checksum_match in hashmatches:
            matches.append(("Modified", checksum_match))

        return matches
