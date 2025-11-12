from config import settings
from parser import Checkpoint, JsonParser, CSVparser, CSVwriter
from ai_setup import AI_Setup
from config import setup_logger
from schema import AgentResponse, Result

logger = setup_logger(__name__, "main.log")


class Application():
    def __init__(self):
        self.json_parser = JsonParser(settings.tweet_json_path)
        # self.csv_parser = CSVparser(settings.extracted_tweet_path)
        self._analyzer=None
    
    @property
    def analyzer(self) -> AI_Setup:
        if self._analyzer is None:
            self._analyzer = AI_Setup()
            logger.info("Gemini analyzer initialized")
        return self._analyzer

    def extract_tweet_from_json(self):
        processed_tweets = self.json_parser.parse()
        return processed_tweets
    
    def write_tweets_from_json_to_csv(self, processed_tweets):
        with CSVwriter(settings.extracted_tweet_path, append=True) as writer:
            writer.write_tweets(processed_tweets)
            
    def read_processed_csv_waiting_for_analysis(self):
        data = CSVparser(settings.extracted_tweet_path)
        return data.parse()
    
    
    def analyze_tweets(self):
        try:
            logger.info(f"Loading tweets from {settings.extracted_tweet_path}")
            parser = CSVparser(settings.extracted_tweet_path)
            tweets = parser.parse()

            if not tweets:
                logger.warning("No tweets found to analyze")
                return Result(success=True, count=0)

            logger.info(f"Loaded {len(tweets)} tweets for analysis")

            analyzed_count = 0
            with Checkpoint(settings.checkpoint_path) as checkpoint:
                start_index = checkpoint.load()
                logger.info(f"Resuming from tweet index {start_index}")

                with CSVwriter(settings.analyzed_tweet_path, append=True) as writer:
                    for i in range(start_index, len(tweets), settings.batch_size):
                        batch = tweets[i : i + settings.batch_size]
                        batch_num = (i // settings.batch_size) + 1
                        total_batches = (
                            len(tweets) + settings.batch_size - 1
                        ) // settings.batch_size

                        logger.info(
                            f"Processing batch {batch_num}/{total_batches} "
                            f"(tweets {i+1}-{min(i+len(batch), len(tweets))} of {len(tweets)})"
                        )

                        for tweet in batch:
                            try:
                                result = self.analyzer.analysis_tweets(tweet.model_dump()) 
                                logger.info(type(result))  
                                validated_result = AgentResponse(**result)
                                logger.debug(f"Tweet {validated_result.id}: {validated_result.should_delete}")
                                analyzed_count += 1

                                if validated_result.should_delete:
                                    #construct a url
                                    data = {}
                                    x_id = validated_result.model_dump()["id"]
                                    url = f"{settings.base_twitter_url}/{settings.x_username}/status/{x_id}"
                                    data["tweet_url"] = url
                                    data["deleted"] = validated_result.model_dump()["should_delete"]
                                    
                                    
                                    writer.write_analysed_tweets(**data)
                            except Exception as e:
                                logger.error(
                                    f"Failed to analyze tweet {tweet.id}: {e}", exc_info=True
                                )
                                return Result(
                                    success=False,
                                    count=analyzed_count,
                                    error_type="analysis_failed",
                                    error_message=str(e),
                                )

                        checkpoint.save(i + len(batch))
                        logger.info(f"Checkpoint saved at index {i + len(batch)}")

            logger.info(f"Analysis complete. Results written to {settings.processed_results_path}")
            return Result(success=True, count=analyzed_count)
        except Exception as e:
            logger.error(f"an error occurred: {e}")
    
    
            
if __name__ == "__main__":
    app = Application()
    # data = app.extract_tweet_from_json()
    # app.write_tweets_from_json_to_csv(data)
    # app.read_processed_csv_waiting_for_analysis()
    app.analyze_tweets()
    